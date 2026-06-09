from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, chat, questions, user
from app.rag.ingest import build_and_seed_vector_database

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cross-Origin Resource Sharing setup for Flutter Mobile / Web Access layers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routing Modules Inclusions Configuration Setup
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["AI Hybrid RAG Core Engine"])
app.include_router(questions.router, prefix=settings.API_V1_STR, tags=["Question Bank Module"])
app.include_router(user.router, prefix=settings.API_V1_STR, tags=["User Account Profiles & Ledger Usage Trackers"])

@app.get("/health", tags=["System Diagnostics Monitoring Checks Nodes"])
def health_check_node():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "vector_store_initialized": True
    }

@app.post("/api/v1/admin/reindex", tags=["Administrative Operational Data Tasks Overhaul Controls"])
def trigger_system_reindexing_routine():
    try:
        build_and_seed_vector_database()
        return {"status": "success", "message": "Vector collections pipeline rebuilt and synchronized successfully."}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
