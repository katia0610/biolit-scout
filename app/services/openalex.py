
import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

OPENALEX_API_URL = "https://api.openalex.org/works"


def search_publications(query: str, per_page: int = 5) -> list[dict]:
    """Search scientific publications using the OpenAlex API."""

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

    data = response.json()
    publications = []

    for item in data.get("results", []):
        authors = [
            authorship.get("author", {}).get("display_name")
            for authorship in item.get("authorships", [])
            if authorship.get("author", {}).get("display_name")
        ]

        publications.append(
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "year": item.get("publication_year"),
                "doi": item.get("doi"),
                "authors": authors,
            }
        )

    return publications
