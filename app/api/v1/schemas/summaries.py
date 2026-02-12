from pydantic import BaseModel, Field, StrictStr, StrictInt
from typing import Dict, Any

class SummarizeRequest(BaseModel):
    text: StrictStr = Field(..., min_length=1, max_length=5000)
    max_length: StrictInt = Field(100, ge=1, le=2000)
    options: Dict[str, Any] = Field(default_factory=dict)