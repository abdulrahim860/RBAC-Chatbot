from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []
