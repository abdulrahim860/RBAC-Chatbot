from fastapi import FastAPI
from app.services.auth import router as auth_router
from app.services.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
