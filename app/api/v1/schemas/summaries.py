from typing import Any, Dict, Literal

from pydantic import BaseModel, Field, StrictInt, StrictStr, ValidationInfo, field_validator

class SummarizeRequest(BaseModel):
    text: StrictStr = Field(..., min_length=1)
    max_length: StrictInt | None = Field(default=None, ge=1)
    summary_type: Literal[
        "tldr",
        "bullet",
        "executive",
        "explain_like_12",
    ] = "tldr"
    length: Literal["short", "medium", "long", "custom"] = "short"
    options: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("max_length")
    @classmethod
    def validate_max_length(cls, value: int | None, info: ValidationInfo) -> int | None:
        if value is None:
            return value

        text = info.data.get("text")

        if text is None:
            return value

        max_allowed = len(text)

        if value > max_allowed:
            raise ValueError(f"max_length must be less than or equal to {max_allowed}")
        return value


class SummarizeResponse(BaseModel):
    summary: StrictStr
    original_text: StrictStr
    summarized_text: StrictStr
    original_character_count: StrictInt
    max_length: StrictInt
    summary_type: Literal[
        "tldr",
        "bullet",
        "executive",
        "explain_like_12",
    ]
    length: Literal["short", "medium", "long", "custom"]
    options: Dict[str, Any]
    provider: StrictStr
    model: StrictStr | None = None
    approach: Literal["langchain", "extractive"]
    fallback_used: bool