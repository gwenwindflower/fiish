from pathlib import Path
from typing import Optional
from typing_extensions import Annotated

from halo import Halo
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from rich.console import Console
import typer

from .answer_query import answer_query
from .format_response import format_response
from .get_issue_comments import get_issue_comments

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
    this = Path(__file__).resolve()
    embedding_function = OpenAIEmbeddings()
    users: list[str] | None = users.split(",") if users else None
    spinner = Halo(text="🚌 Off to the bait shop (takes awhile)...", spinner="moon")

    spinner.start()
    get_issue_comments(repo_owner, repo_name, users)

    issue_comments_data_path = this.parent / "issue_comments.csv"
    loader: CSVLoader = CSVLoader(
        file_path=issue_comments_data_path,
        metadata_columns=["user", "updated_at", "issue_url"],
        source_column="issue_url",
    )
    docs = loader.load()

    db: Chroma = Chroma.from_documents(
        docs, embedding_function, persist_directory="./chroma_db"
    )
    spinner.stop_and_persist(symbol="🪣", text="Ready to fish!")


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
