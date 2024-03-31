from fastapi import FastAPI
from .answer_query import answer_query

app: FastAPI = FastAPI()


@app.get("/")
async def query(query: str, temperature: float, fast: bool):
    return answer_query(query, temperature, fast)
