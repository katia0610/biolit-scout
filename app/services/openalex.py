import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

OPENALEX_API_URL = "https://api.openalex.org/works"


def reconstruct_abstract(
    abstract_index: dict | None,
) -> str | None:
    """Reconstruct an abstract from OpenAlex's inverted index."""

    if not abstract_index:
        return None

    words = {}

    for word, positions in abstract_index.items():
        for position in positions:
            words[position] = word

    if not words:
        return None

    return " ".join(
        words[position] for position in sorted(words)
    )


def search_publications(
    query: str,
    per_page: int = 5,
) -> list[dict]:
    """Search scientific publications using OpenAlex."""

    api_key = os.getenv("OPENALEX_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAlex API key is not configured.",
        )

    params = {
        "search": query,
        "per_page": per_page,
        "api_key": api_key,
    }

    try:
        response = httpx.get(
            OPENALEX_API_URL,
            params=params,
            timeout=15.0,
        )
        response.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="OpenAlex request timed out.",
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="OpenAlex returned an error.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to OpenAlex.",
        )

    try:
        data = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="OpenAlex returned an invalid response.",
        )

    publications = []

    for item in data.get("results", []):
        authors = [
            authorship.get("author", {}).get("display_name")
            for authorship in item.get("authorships", [])
            if authorship.get("author", {}).get("display_name")
        ]

        location = item.get("primary_location") or {}
        source = location.get("source") or {}

        publications.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "year": item.get("publication_year"),
                "doi": item.get("doi"),
                "authors": authors,
                "abstract": reconstruct_abstract(
                    item.get("abstract_inverted_index")
                ),
                "journal": source.get("display_name"),
                "url": location.get("landing_page_url"),
            }
        )

    return publications