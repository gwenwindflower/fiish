from fastapi import FastAPI
from .answer_query import answer_query

app: FastAPI = FastAPI()


@app.get("/")
async def query(query: str, temperature: float = 0.5, fast: bool = False):
    return answer_query(query, temperature, fast)
