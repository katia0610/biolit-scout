# BioLit Scout

**AI-powered scientific literature discovery — CI/CD project**

BioLit Scout is a project designed to explore scientific literature discovery and analysis using AI. The current version provides a FastAPI backend and an automated CI/CD pipeline, establishing the foundation for future AI agent capabilities.

## Features

- **REST API:** FastAPI endpoints for health checks and service information.
- **Automated testing:** Pytest and FastAPI TestClient.
- **Containerization:** Docker image built from Python 3.12.
- **Continuous Integration (CI):** GitHub Actions automatically runs tests on pushes and pull requests targeting `main`.
- **Container Registry:** Docker images are published to GitHub Container Registry (GHCR).
- **Continuous Deployment (CD):** Successful pushes to `main` trigger a Render deployment.
- **Post-deployment verification:** GitHub Actions checks that the deployed API responds successfully.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Testing | Pytest, HTTPX |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Container registry | GitHub Container Registry |
| Deployment | Render |

## Project Structure

```text
biolit-scout/
├── app/
│   └── main.py
├── tests/
│   └── test_main.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns service information |
| GET | `/health` | Checks API availability |
| GET | `/docs` | Interactive Swagger API documentation |

**Production health check:** https://biolit-scout.onrender.com/health

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/katia0610/biolit-scout.git
cd biolit-scout
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run automated tests

```bash
python -m pytest -v
```

The current test suite contains two tests covering the `/` and `/health` endpoints.

### 5. Run the API locally

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Interactive documentation: `http://127.0.0.1:8000/docs`

## Docker

### Build the image

```bash
docker build -t biolit-scout .
```

### Run the container

```bash
docker run --rm -p 8000:8000 biolit-scout
```

The API is then available at `http://localhost:8000`.

## CI/CD Pipeline

The workflow is defined in `.github/workflows/ci.yml`.

```text
Push to main
     |
     v
GitHub Actions
     |
     v
Install dependencies
     |
     v
Run Pytest
     |
     v
Build Docker image
     |
     v
Publish image to GHCR
     |
     v
Trigger Render deployment
     |
     v
Check deployed API health
```

### Pipeline details

1. **Checkout:** Retrieves the repository source code.
2. **Python setup:** Configures Python 3.12 and installs dependencies.
3. **Testing:** Runs the automated test suite.
4. **Docker build:** Builds the application image using Docker Buildx.
5. **Image publishing:** On pushes to `main`, publishes the image to GHCR.
6. **Deployment:** Calls a Render Deploy Hook after publishing the image.
7. **Smoke test:** Retries the `/health` request until the API responds successfully or the retry limit is reached.

Pull requests run the tests and build the image without publishing it or triggering deployment.

### Container image

```text
ghcr.io/katia0610/biolit-scout:latest
```

The pipeline also publishes an image tagged with the Git commit SHA.

The Render deployment hook URL is stored securely in GitHub Actions Secrets as `RENDER_DEPLOY_HOOK_URL`.

## Current Status

- [x] FastAPI application initialized
- [x] Automated API tests implemented
- [x] Docker image built and tested locally
- [x] GitHub Actions workflow configured
- [x] Docker image published to GHCR
- [x] Render deployment automated
- [x] Post-deployment smoke test implemented
- [ ] Scientific publication search and AI analysis features

**Next objective:** Develop the scientific literature discovery agent, including publication retrieval, research-question analysis, and evidence-based comparisons of scientific studies.

## Repository

GitHub: https://github.com/katia0610/biolit-scout
