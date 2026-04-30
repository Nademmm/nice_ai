from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import router as chat_router
from app.api.upload import router as upload_router
from app.services.rag_service import rag_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Initialize knowledge base (runs in background)
    import threading
    def load_kb():
        try:
            rag_service.initialize_default_knowledge()
            print("[LIFESPAN] Knowledge base initialized successfully")
        except Exception as e:
            print(f"[LIFESPAN] Error initializing knowledge base: {str(e)}")
    
    kb_thread = threading.Thread(target=load_kb, daemon=True)
    kb_thread.start()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered RAG Chatbot API for CV Niscahya Indonesia Cerdas",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(upload_router, prefix="/api", tags=["Upload"])

dashboard_dir = Path(__file__).resolve().parent / "dashboard"
app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")

chat_test_dir = Path(__file__).resolve().parent / "chat_test"
app.mount("/chat-test", StaticFiles(directory=chat_test_dir, html=True), name="chat-test")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "dashboard": "/dashboard",
        "chat_test": "/chat-test"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
