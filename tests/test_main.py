import json
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services.groq_analysis import analyze_publications
from app.services.openalex import reconstruct_abstract


client = TestClient(app)


SAMPLE_PUBLICATION = {
    "id": "https://openalex.org/W123",
    "title": "Cell Segmentation Using Deep Learning",
    "year": 2025,
    "doi": "https://doi.org/10.1234/example",
    "authors": ["Alice Smith"],
    "abstract": "Cell segmentation improves biological image analysis.",
    "journal": "Example Journal",
    "url": "https://example.org/article",
}


SAMPLE_ANALYSIS = {
    "id": "https://openalex.org/W123",
    "objective": "Study cell segmentation.",
    "methodology": "The abstract does not specify the method.",
    "main_findings": "The abstract reports improved analysis.",
    "limitations": "Not specified in the abstract.",
    "relevance_to_query": "Directly relevant to cell segmentation.",
}


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["version"] == "0.3.0"


def test_search_publications():
    with patch(
        "app.main.search_publications",
        return_value=[SAMPLE_PUBLICATION],
    ) as mock_search:
        response = client.get(
            "/search",
            params={"q": "cell segmentation", "limit": 5},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["publications"][0]["abstract"] == (
        SAMPLE_PUBLICATION["abstract"]
    )
    mock_search.assert_called_once_with(
        query="cell segmentation",
        per_page=5,
    )


def test_search_requires_query():
    response = client.get("/search")

    assert response.status_code == 422


def test_search_rejects_invalid_limit():
    response = client.get(
        "/search",
        params={"q": "cell segmentation", "limit": 20},
    )

    assert response.status_code == 422


def test_analyze_endpoint():
    publication_without_abstract = {
        **SAMPLE_PUBLICATION,
        "id": "https://openalex.org/W456",
        "title": "Article without abstract",
        "abstract": None,
    }

    with (
        patch(
            "app.main.search_publications",
            return_value=[
                SAMPLE_PUBLICATION,
                publication_without_abstract,
            ],
        ),
        patch(
            "app.main.analyze_publications",
            return_value={
                "articles": [SAMPLE_ANALYSIS],
                "comparative_synthesis": "One abstract was analyzed.",
                "research_gaps": ["Investigate other datasets."],
            },
        ) as mock_analysis,
    ):
        response = client.post(
            "/analyze",
            json={"q": "cell segmentation", "limit": 2},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["searched_count"] == 2
    assert data["analyzed_count"] == 1
    assert data["publications"][0]["analysis"]["objective"] == (
        SAMPLE_ANALYSIS["objective"]
    )
    assert data["publications"][1]["analysis"] is None
    assert data["research_gaps"] == [
        "Investigate other datasets."
    ]

    mock_analysis.assert_called_once_with(
        query="cell segmentation",
        publications=[SAMPLE_PUBLICATION],
    )


def test_analyze_without_abstracts_skips_groq():
    publication = {
        **SAMPLE_PUBLICATION,
        "abstract": None,
    }

    with (
        patch(
            "app.main.search_publications",
            return_value=[publication],
        ),
        patch("app.main.analyze_publications") as mock_analysis,
    ):
        response = client.post(
            "/analyze",
            json={"q": "cell segmentation"},
        )

    assert response.status_code == 200
    assert response.json()["analyzed_count"] == 0
    assert response.json()["publications"][0]["analysis"] is None
    mock_analysis.assert_not_called()


def test_analyze_rejects_invalid_request():
    response = client.post(
        "/analyze",
        json={"q": "x", "limit": 10},
    )

    assert response.status_code == 422


def test_reconstruct_abstract():
    abstract_index = {
        "Cell": [0],
        "segmentation": [1],
        "improves": [2],
        "analysis": [3],
    }

    assert reconstruct_abstract(abstract_index) == (
        "Cell segmentation improves analysis"
    )


def test_reconstruct_abstract_when_missing():
    assert reconstruct_abstract(None) is None
    assert reconstruct_abstract({}) is None


def test_groq_analysis_success(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    groq_result = {
        "articles": [SAMPLE_ANALYSIS],
        "comparative_synthesis": "A short comparison.",
        "research_gaps": ["More experiments are needed."],
    }

    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(groq_result),
                }
            }
        ]
    }

    with patch(
        "app.services.groq_analysis.httpx.post",
        return_value=mock_response,
    ) as mock_post:
        result = analyze_publications(
            query="cell segmentation",
            publications=[SAMPLE_PUBLICATION],
        )

    assert result == groq_result
    mock_response.raise_for_status.assert_called_once()

    request_kwargs = mock_post.call_args.kwargs
    assert request_kwargs["headers"]["Authorization"] == (
        "Bearer test-key"
    )
    assert request_kwargs["json"]["model"] == (
        "openai/gpt-oss-20b"
    )


def test_groq_missing_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(HTTPException) as error:
        analyze_publications(
            query="cell segmentation",
            publications=[SAMPLE_PUBLICATION],
        )

    assert error.value.status_code == 503