import shutil
from pathlib import Path

from fastapi import FastAPI

from .answer_query import answer_query
from .build_vector_store import build_vector_store

app: FastAPI = FastAPI()


@app.get("/")
async def go(query: str, temperature: float = 0.5, fast: bool = False):
    """
    Endpoint to return the answer to a query.
    """
    return answer_query(query, temperature, fast)


@app.get("/bait")
async def bait(repo_owner: str, repo_name: str, users: str | None = None):
    """
    Refresh the vector store.
    """
    userList: list[str] | None = users.split(",") if users else None
    build_vector_store(repo_owner, repo_name, userList)


@app.get("/clean")
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
