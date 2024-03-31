from fastapi import FastAPI
from .main import answer_query

app = FastAPI()


@app.get("/")
async def query(query: str, refresh: bool = False):
    return answer_query(query, refresh)
