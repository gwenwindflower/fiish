import os
from operator import itemgetter

from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings

SYSTEM: str = """
    You're a kind and helpful language model trained to help surface existing issues in an open source GitHub repository.
    You can retrieve and summarize relevant information from the issues to help answer questions about them.
    Please communicate primarily in lists that summarize the relevant isssues, and make sure to reference the issue number of the issue you're referencing.
    Conclude with a paragraph summarizing the various issues, and pros and cons of any solutions mentioned.
    """
HUMAN: str = """
    Considering these relevant issues as context:
    {context}

    What existing issues and discussion are there around this question:
    {query}
    """


def get_retriever():
    embedding_function = OpenAIEmbeddings()
    db: Chroma = Chroma(
        persist_directory="./chroma_db", embedding_function=embedding_function
    )
    return db.as_retriever(search_kwargs={"k": 6})


def answer_query(
    query: str, temperature: float, fast: bool = False, trace: bool = False
):
    # Enable LangSmith for introspecting the chains
    if trace:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"

    # LLM
    model_claude: ChatAnthropic = ChatAnthropic(
        model_name="claude-3-opus-20240229", temperature=temperature
    )
    # If you want to Go Fast you can use Groq instead of Claude, just change the model in the pipeline
    model_groq: ChatGroq = ChatGroq(model="gemma-7b-it", temperature=temperature)

    if fast:
        model = model_groq
    else:
        model = model_claude
    # Input
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
        [("system", SYSTEM), ("human", HUMAN)]
    )
    # Vector Store
    retriever = get_retriever()
    setup_and_retrieval: RunnableParallel = RunnableParallel(
        {
            "context": retriever,
            "query": RunnablePassthrough(),
        }
    )
    # Output
    model_output_with_references: RunnableParallel = RunnableParallel(
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
