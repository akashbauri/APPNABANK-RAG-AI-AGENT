from pydantic import BaseModel, EmailStr
from typing import Optional, List

class Token(BaseModel):
    access_token: str
    token_type: str

class GoogleLoginRequest(BaseModel):
    id_token: str

class ChatRequest(BaseModel):
    question: str
    age: Optional[int] = None
    monthly_income: Optional[float] = None
    goal: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    source_type: str
    source_name: str
    detected_language: str
    free_limit_reached: bool

class QuestionResponse(BaseModel):
    id: str
    category: str
    question: str
    language: str

class UserProfileResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    language_preference: str
    query_count: int
