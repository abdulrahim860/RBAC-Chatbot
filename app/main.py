from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers
from app.services.auth import router as auth_router
from app.services.chat import router as chat_router

# Initialize the FastAPI app
app = FastAPI(
    title="RBAC Chatbot",
    description="RBAC-protected chatbot API for FinSolve Technologies",
    version="1.0.0"
)

# CORS settings for allowing frontend (Streamlit at http://localhost:8501) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the authentication and chat routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

# Health-check route (optional) to quickly verify the service is up
@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok"}
