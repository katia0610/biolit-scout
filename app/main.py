
from fastapi import FastAPI, Query

from app.services.openalex import search_publications

app = FastAPI(
    title="BioLit Scout",
    description="AI-powered scientific literature discovery agent",
    version="0.2.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "BioLit Scout"}


@app.get("/")
def root():
    return {
        "message": "Welcome to BioLit Scout",
        "purpose": "Discover and analyze scientific publications",
    }


@app.get("/search")
def search(
    q: str = Query(
        ...,
        min_length=2,
        max_length=300,
        description="Scientific research question or keywords",
    ),
    limit: int = Query(default=5, ge=1, le=10),
):
    publications = search_publications(query=q, per_page=limit)

    return {
        "query": q,
        "count": len(publications),
        "publications": publications,
    }
