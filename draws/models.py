from pydantic import BaseModel
from typing import List, Optional

class Draw(BaseModel):
    draw_id: int
    status: str  # open, closed, completed
    participants: List[str]
    ledger_hash: Optional[str] = None
    winner: Optional[str] = None
    timestamp: str
