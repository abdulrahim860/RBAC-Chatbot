from fastapi import APIRouter, Depends
from app.services.auth import authenticate
from app.schemas import ChatRequest
from app.utils.rag import get_response

router = APIRouter()

@router.post("/")
def chat(req: ChatRequest, user=Depends(authenticate)):
    return {"response": get_response(req.message, user["role"])}
