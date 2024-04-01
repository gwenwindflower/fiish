from pathlib import Path

from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from .get_issue_comments import get_issue_comments
from .write_csv import write_csv


def build_vector_store(
    repo_owner: str, repo_name: str, userList: list[str] | None
) -> None:
    """
    Build the vector store from the scraped issue comments in the bait shop.
    """
    embedding_function = OpenAIEmbeddings()
    comments = get_issue_comments(repo_owner, repo_name, userList)
    issue_comments_data_path: Path = write_csv(comments)
    loader: CSVLoader = CSVLoader(
        file_path=issue_comments_data_path,
        metadata_columns=["user", "updated_at", "issue_url"],
        source_column="issue_url",
    )
    docs = loader.load()

    Chroma.from_documents(docs, embedding_function, persist_directory="./chroma_db")
