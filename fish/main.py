import argparse
import os
from operator import itemgetter
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_openai import OpenAIEmbeddings

from .get_issue_comments import get_issue_comments

SYSTEM: str = """
    You're a kind an helpful language model trained to help surface existing issues in the dbt-core GitHub repository.
    You can retrieve and summarize relevant information from the issues to help answer questions about them.
    """
HUMAN: str = """
    Considering these relevant issues as context:
    {context}

    How would you respond to this?
    {query}
    """


# Main functions
def load_retriever(refresh: bool = False):
    embedding_function = OpenAIEmbeddings()
    if refresh:
        this = Path(__file__).resolve()
        issue_comments_data_path = this.parent / "issue_comments.csv"
        loader = CSVLoader(
            file_path=issue_comments_data_path,
            metadata_columns=["user", "updated_at", "issue_url"],
            source_column="issue_url",
        )
        docs = loader.load()

        db: Chroma = Chroma.from_documents(
            docs, embedding_function, persist_directory="./chroma_db"
        )
        return db.as_retriever()
    else:
        db = Chroma(
            persist_directory="./chroma_db", embedding_function=embedding_function
        )
        return db.as_retriever()


def answer_query(query: str, refresh: bool = False):
    # Enable LangSmith for introspecting the chains
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

    # LLM
    model: ChatAnthropic = ChatAnthropic(
        model_name="claude-3-opus-20240229", temperature=0.5
    )

    ## Input
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [("system", SYSTEM), ("human", HUMAN)]
    )
    ## Vector Store
    retriever = load_retriever(refresh=refresh)
    setup_and_retrieval = RunnableParallel(
        {
            "context": retriever,
            "query": RunnablePassthrough(),
        }
    )
    ## Output
    model_output_with_references = RunnableParallel(
        {
            "model_output": {
                "query": itemgetter("query"),
                "context": itemgetter("context"),
            }
            | prompt
            | model
            | StrOutputParser(),
            "references": itemgetter("context"),
        }
    )
    chain = setup_and_retrieval | model_output_with_references
    return chain.invoke(query)


def main():
    # CLI
    parser = argparse.ArgumentParser(
        description="Ask a question to the dbt-core issues history"
    )
    parser.add_argument("query", type=str, help="Question you want to answer")
    parser.add_argument(
        "--refresh", action="store_true", help="Refresh the vector store"
    )
    args = parser.parse_args()
    if args.refresh:
        get_issue_comments()
    answer = answer_query(args.query, refresh=args.refresh)
    model_output = answer["model_output"]
    referenced_issues = answer["references"]
    issue_comments: str = ""
    for issue in referenced_issues:
        issue_comments += f"""
             --------------------------

             ### {issue.metadata['issue_url']} from {issue.metadata['user']} at {issue.metadata['updated_at']}
             {issue.page_content}
             
             --------------------------
        """
    print(f"""
        # Summary
        {model_output }
        ## Based on these issue comments:
        {issue_comments}
    """)


if __name__ == "__main__":
    main()
