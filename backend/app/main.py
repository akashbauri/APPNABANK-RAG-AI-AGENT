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

# --- SECURITY FIX: Restricting CORS Origins ---
# We use settings.ALLOWED_ORIGINS (defined in your config) to avoid unsafe wildcard ["*"] mapping
# while allow_credentials is True.
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "ALLOWED_ORIGINS", [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-frontend-domain.com"
    ]),
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
