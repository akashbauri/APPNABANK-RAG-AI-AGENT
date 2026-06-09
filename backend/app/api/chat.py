from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token
from app.database.supabase_client import supabase
from app.models.schemas import ChatRequest, ChatResponse
from app.rag.pipeline import rag_pipeline
from app.services.voice_service import voice_service
from typing import Optional

router = APIRouter()
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session verification token.")
    return payload["sub"]

def enforce_usage_and_update(user_id: str) -> bool:
    user_res = supabase.table("users").select("query_count").eq("user_id", user_id).execute()
    if not user_res.data:
        raise HTTPException(status_code=404, detail="User account record instance tracking node entry not discovered.")
    
    current_count = user_res.data[0]["query_count"]
    if current_count >= 20:
        return True # Limit breached condition met indicator
        
    supabase.table("users").update({"query_count": current_count + 1}).eq("user_id", user_id).execute()
    return False

@router.post("/chat", response_model=ChatResponse)
def handle_text_chat(payload: ChatRequest, user_id: str = Depends(get_current_user_id)):
    limit_reached = enforce_usage_and_update(user_id)
    if limit_reached:
        return ChatResponse(
            answer="Your free limit has been reached. Recharge ₹10 to continue.",
            source_type="system",
            source_name="Billing Engine",
            detected_language="en",
            free_limit_reached=True
        )

    profile_context = {}
    if payload.age or payload.monthly_income or payload.goal:
        profile_context = {
            "age": payload.age,
            "monthly_income": payload.monthly_income,
            "goal": payload.goal
        }

    rag_result = rag_pipeline.process_query(payload.question, profile_data=profile_context)

    # Track interaction event within standard auditing timeline structure tables
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "question": payload.question,
        "answer": rag_result["answer"],
        "source_type": rag_result["source_type"],
        "source_name": rag_result["source_name"]
    }).execute()

    # Log operational payload metadata ledger entry
    supabase.table("query_usage").insert({
        "user_id": user_id,
        "action_type": "text_chat"
    }).execute()

    return ChatResponse(
        answer=rag_result["answer"],
        source_type=rag_result["source_type"],
        source_name=rag_result["source_name"],
        detected_language=rag_result["detected_language"],
        free_limit_reached=False
    )

@router.post("/voice-chat")
async def handle_voice_chat(
    file: UploadFile = File(...),
    age: Optional[int] = Form(None),
    monthly_income: Optional[float] = Form(None),
    goal: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user_id)
):
    limit_reached = enforce_usage_and_update(user_id)
    if limit_reached:
        return {
            "recognized_text": "",
            "answer": "Your free limit has been reached. Recharge ₹10 to continue.",
            "source_type": "system",
            "source_name": "Billing Engine",
            "detected_language": "en",
            "free_limit_reached": True
        }

    # Transcribe Speech file dynamically
    recognized_text = await voice_service.speech_to_text(file)

    profile_context = {}
    if age or monthly_income or goal:
        profile_context = {"age": age, "monthly_income": monthly_income, "goal": goal}

    rag_result = rag_pipeline.process_query(recognized_text, profile_data=profile_context)

    # Save to history
    supabase.table("chat_history").insert({
        "user_id": user_id,
        "question": recognized_text,
        "answer": rag_result["answer"],
        "source_type": rag_result["source_type"],
        "source_name": rag_result["source_name"]
    }).execute()

    supabase.table("query_usage").insert({
        "user_id": user_id,
        "action_type": "voice_chat"
    }).execute()

    return {
        "recognized_text": recognized_text,
        "answer": rag_result["answer"],
        "source_type": rag_result["source_type"],
        "source_name": rag_result["source_name"],
        "detected_language": rag_result["detected_language"],
        "free_limit_reached": False
    }
