import shutil
from pathlib import Path
from typing import Optional

import typer
from halo import Halo
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from rich.console import Console
from typing_extensions import Annotated

from .answer_query import answer_query
from .format_response import format_response
from .get_issue_comments import get_issue_comments
from .write_csv import write_csv

cli = typer.Typer()


@cli.command()
def bait(
    repo_owner: str,
    repo_name: str,
    users: Annotated[Optional[str], typer.Argument()] = None,
):
    """
    Head to the bait shop: collect issue comments from a GitHub repository for the vector store.
    """
    embedding_function = OpenAIEmbeddings()
    users: list[str] | None = users.split(",") if users else None
    spinner = Halo(text="🚌 Off to the bait shop (takes awhile)...", spinner="moon")

    spinner.start()
    comments = get_issue_comments(repo_owner, repo_name, users)
    issue_comments_data_path: Path = write_csv(comments)
    loader: CSVLoader = CSVLoader(
        file_path=issue_comments_data_path,
        metadata_columns=["user", "updated_at", "issue_url"],
        source_column="issue_url",
    )
    docs = loader.load()

    Chroma.from_documents(docs, embedding_function, persist_directory="./chroma_db")
    spinner.stop_and_persist(symbol="🪣", text="Ready to fish!")


@cli.command()
def clean():
    vector_store_path = Path(__file__).resolve().parent.parent / "chroma_db"
    if vector_store_path.exists() and vector_store_path.is_dir():
        shutil.rmtree(vector_store_path)
        print("🧼✨Vector store has been removed. Run `fiish bait` to start fresh!")
    else:
        print("❌🙈 No vector store to remove.")


@cli.command()
def go(
    query: str,
    temp: Annotated[float, typer.Option()] = 0.5,
    fast: Annotated[bool, typer.Option()] = False,
):
    """
    Go fishing: answer a query about existing issues in an open source GitHub repository.
    You can control the `--temperature` and go `--fast` via Groq if you want.
    """
    spinner = Halo(text="🎣 Gone fishin'...", spinner="moon")
    spinner.start()
    answer: dict[str, str] = answer_query(query, temp, fast)
    summary_panel, references_panel = format_response(answer)
    spinner.stop_and_persist(symbol="🐟", text="Caught one!")
    console: Console = Console()
    console.print(summary_panel)
    console.print(references_panel)
