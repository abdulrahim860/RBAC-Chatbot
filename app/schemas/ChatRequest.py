from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    use_history: Optional[bool] = True
    history: Optional[List[dict]] = []
