from pydantic import BaseModel
from typing import List, Optional

# Define the structure of the chat request received from the frontend
class ChatRequest(BaseModel):
    message: str
    use_history: Optional[bool] = True
    history: Optional[List[dict]] = []