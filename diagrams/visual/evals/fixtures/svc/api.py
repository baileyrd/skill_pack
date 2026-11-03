"""HTTP layer: FastAPI routes for the link shortener."""
from fastapi import FastAPI, HTTPException

from svc import store, codes

app = FastAPI()


@app.post("/links")
def create(url: str) -> dict[str, str]:
    code = codes.new_code()
    store.save(code, url)
    return {"code": code}


@app.get("/{code}")
def resolve(code: str) -> dict[str, str]:
    url = store.load(code)
    if url is None:
        raise HTTPException(404)
    store.count_hit(code)
    return {"url": url}
