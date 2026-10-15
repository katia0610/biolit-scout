
from fastapi import FastAPI

app = FastAPI(
    title="BioLit Scout",
    description="AI-powered scientific literature discovery agent",
    version="0.1.0",
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
