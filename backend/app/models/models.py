from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    whatsapp = Column(String(50), nullable=False)
    project_needs = Column(Text, nullable=True)
    status = Column(String(50), default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    product_recommended = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
