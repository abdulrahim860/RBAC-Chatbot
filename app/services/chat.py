from fastapi import APIRouter, Depends
from app.services.auth import authenticate
from app.schemas.ChatRequest import ChatRequest
from app.utils.rag import get_response

router = APIRouter()

@router.post("/")
def chat(req: ChatRequest, user=Depends(authenticate)):
    use_history = bool(req.history and len(req.history) > 0)
    result = get_response(req.message, user["role"],req.history or [], use_history)
    return {
        "response": result["answer"],
        "sources": result["sources"]
    }