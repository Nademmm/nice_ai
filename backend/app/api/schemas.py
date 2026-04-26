from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    answer: str
    intent: str
    product: Optional[dict] = None


class LeadCreate(BaseModel):
    name: str
    whatsapp: str
    project_needs: Optional[str] = None


class LeadResponse(BaseModel):
    id: int
    name: str
    whatsapp: str
    project_needs: Optional[str]
    status: str
    created_at: str

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    filename: str
    status: str
    documents_added: int
    message: str
