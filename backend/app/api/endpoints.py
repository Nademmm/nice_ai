from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.schemas import ChatRequest, ChatResponse, LeadCreate, LeadResponse
from app.services.rag_service import rag_service
from app.core.database import get_db
from app.models.models import Lead, ChatHistory

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = await rag_service.process_message(
            message=request.message,
            session_id=request.session_id
        )

        chat_record = ChatHistory(
            session_id=request.session_id,
            message=request.message,
            response=result["answer"],
            intent=result["intent"],
            product_recommended=result["product"]["name"] if result["product"] else None
        )
        db.add(chat_record)
        db.commit()

        return ChatResponse(
            answer=result["answer"],
            intent=result["intent"],
            product=result["product"]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lead", response_model=LeadResponse)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    try:
        db_lead = Lead(
            name=lead.name,
            whatsapp=lead.whatsapp,
            project_needs=lead.project_needs,
            status="new"
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)

        return LeadResponse(
            id=db_lead.id,
            name=db_lead.name,
            whatsapp=db_lead.whatsapp,
            project_needs=db_lead.project_needs,
            status=db_lead.status,
            created_at=str(db_lead.created_at)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads", response_model=List[LeadResponse])
async def get_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return [
        LeadResponse(
            id=lead.id,
            name=lead.name,
            whatsapp=lead.whatsapp,
            project_needs=lead.project_needs,
            status=lead.status,
            created_at=str(lead.created_at)
        )
        for lead in leads
    ]


@router.get("/history")
async def get_history(session_id: str = "default", limit: int = 50, db: Session = Depends(get_db)):
    history = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id
    ).order_by(
        ChatHistory.created_at.desc()
    ).limit(limit).all()

    return [
        {
            "id": chat.id,
            "message": chat.message,
            "response": chat.response,
            "intent": chat.intent,
            "product_recommended": chat.product_recommended,
            "created_at": str(chat.created_at)
        }
        for chat in reversed(history)
    ]


@router.delete("/history")
async def clear_history(session_id: str = "default", db: Session = Depends(get_db)):
    db.query(ChatHistory).filter(ChatHistory.session_id == session_id).delete()
    db.commit()
    return {"message": "History cleared"}
