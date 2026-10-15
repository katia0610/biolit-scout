
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "BioLit Scout",
    }


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Welcome to BioLit Scout"
    assert "purpose" in data


from unittest.mock import patch


def test_search_publications():
    mock_publications = [
        {
            "id": "https://openalex.org/W123",
            "title": "Cell Segmentation Using Deep Learning",
            "year": 2025,
            "doi": "https://doi.org/10.1234/example",
            "authors": ["Alice Smith"],
        }
    ]

    with patch(
        "app.main.search_publications",
        return_value=mock_publications,
    ) as mock_search:
        response = client.get(
            "/search",
            params={"q": "cell segmentation", "limit": 5},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "cell segmentation"
    assert data["count"] == 1
    assert data["publications"][0]["title"] == (
        "Cell Segmentation Using Deep Learning"
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
