import shutil
from pathlib import Path
from typing import Optional

import typer
from halo import Halo
from rich.console import Console
from typing_extensions import Annotated

from .answer_query import answer_query
from .format_response import format_response
from .build_vector_store import build_vector_store

cli = typer.Typer()


@cli.command()
def bait(
    repo_owner: str = typer.Argument(
        help="The owner (user/organization) of the GitHub repo to scrape"
    ),
    repo_name: str = typer.Argument(help="The name of the repo to scrape"),
    users: Optional[str] = typer.Argument(
        help="An optional list of comma-separated user ids to filter the issue comments on",
        default=None,
    ),
):
    """
    Head to the bait shop: collect issue comments from a GitHub repository for the vector store.
    """
    userList: list[str] | None = users.split(",") if users else None
    spinner = Halo(text="🚌 Off to the bait shop (takes awhile)...", spinner="moon")
    spinner.start()

    build_vector_store(repo_owner, repo_name, userList)

    spinner.stop_and_persist(symbol="🪣", text="Ready to fish!")


@cli.command()
def clean():
    """
    Clean up the vector store: remove all files and directories in the vector store.
    """
    vector_store_path = Path(__file__).resolve().parent.parent / "chroma_db"
    if vector_store_path.exists() and vector_store_path.is_dir():
        shutil.rmtree(vector_store_path)
        print("🧼✨Vector store has been removed. Run `fiish bait` to start fresh!")
    else:
        print("❌🙈 No vector store to remove.")


@cli.command()
def go(
    query: str,
    temp: Annotated[
        float,
        typer.Option(
            help="Control the creativity of a the model response with a float between 0 and 1"
        ),
    ] = 0.5,
    fast: Annotated[
        bool,
        typer.Option(
            help="Go fast with Groq running Gemma, you must have a GROQ_API_KEY for this to work"
        ),
    ] = False,
    trace: Annotated[
        bool, typer.Option(help="For dev use, this turns on LangSmith tracing")
    ] = False,
):
    """
    Go fishing: answer a query about existing issues in an open source GitHub repository.
    You can control the `--temperature` and go `--fast` via Groq if you want.
    """
    spinner = Halo(text="🎣 Gone fishin'...", spinner="moon")
    spinner.start()

    answer: dict[str, str] = answer_query(query, temp, fast, trace)

    summary_panel, references_panel = format_response(answer)

    spinner.stop_and_persist(symbol="🐟", text="Caught one!")

    console: Console = Console()
    console.print(summary_panel)
    console.print(references_panel)
