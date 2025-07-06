from fastapi import APIRouter, Depends
from backend.services.auth import authenticate
from backend.schemas.ChatRequest import ChatRequest
from backend.utils.rag import get_response

# Initialize a router for handling chat-related API routes
router = APIRouter()

# POST endpoint for handling chat requests
@router.post("/")
def chat(req: ChatRequest, user=Depends(authenticate)):
    use_history = bool(req.history and len(req.history) > 0)
    result = get_response(req.message, user["role"],req.history or [], use_history)
    return {
        "response": result["answer"],
        "sources": result["sources"]
    }