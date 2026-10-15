from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from app.services.openalex import search_publications
from app.services.groq_analysis import analyze_publications


app = FastAPI(
    title="BioLit Scout",
    description=(
        "Scientific literature discovery, analysis "
        "and comparison using OpenAlex and Groq."
    ),
    version="0.3.0",
)


class AnalysisRequest(BaseModel):
    q: str = Field(
        ...,
        min_length=2,
        max_length=300,
        description="Scientific research question or keywords",
    )
    limit: int = Field(default=5, ge=1, le=5)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "BioLit Scout",
        "version": "0.3.0",
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to BioLit Scout",
        "purpose": (
            "Discover, analyze and compare scientific publications"
        ),
        "version": "0.3.0",
        "endpoints": {
            "health": "/health",
            "search": "/search",
            "analysis": "/analyze",
            "documentation": "/docs",
        },
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
    publications = search_publications(
        query=q,
        per_page=limit,
    )

    return {
        "query": q,
        "count": len(publications),
        "publications": publications,
    }


@app.post("/analyze")
def analyze(request: AnalysisRequest):
    publications = search_publications(
        query=request.q,
        per_page=request.limit,
    )

    publications_with_abstracts = [
        publication
        for publication in publications
        if (publication.get("abstract") or "").strip()
    ]

    if not publications_with_abstracts:
        return {
            "query": request.q,
            "searched_count": len(publications),
            "analyzed_count": 0,
            "publications": [
                {**publication, "analysis": None}
                for publication in publications
            ],
            "comparative_synthesis": None,
            "research_gaps": [],
            "message": (
                "No abstracts were available for analysis."
            ),
        }

    ai_result = analyze_publications(
        query=request.q,
        publications=publications_with_abstracts,
    )

    # Accept analyses only for publications actually retrieved.
    valid_ids = {
        publication.get("id")
        for publication in publications_with_abstracts
    }

    analyses_by_id = {
        analysis.get("id"): analysis
        for analysis in ai_result.get("articles", [])
        if (
            isinstance(analysis, dict)
            and analysis.get("id") in valid_ids
        )
    }

    enriched_publications = [
        {
            **publication,
            "analysis": analyses_by_id.get(publication.get("id")),
        }
        for publication in publications
    ]

    return {
        "query": request.q,
        "searched_count": len(publications),
        "analyzed_count": len(analyses_by_id),
        "publications": enriched_publications,
        "comparative_synthesis": ai_result.get(
            "comparative_synthesis"
        ),
        "research_gaps": ai_result.get("research_gaps", []),
        "message": (
            "Analysis is based on available abstracts, "
            "not necessarily full-text articles."
        ),
    }