from typing import Any, Dict, Literal

from pydantic import BaseModel, Field, StrictInt, StrictStr

class SummarizeRequest(BaseModel):
    text: StrictStr = Field(..., min_length=1, max_length=5000)
    max_length: StrictInt | None = Field(default=None, ge=1, le=2000)
    summary_type: Literal[
        "tldr",
        "bullet",
        "executive",
        "action_items",
        "explain_like_12",
    ] = "tldr"
    length: Literal["short", "medium", "long"] = "short"
    options: Dict[str, Any] = Field(default_factory=dict)