from datetime import datetime

from pydantic import BaseModel, ConfigDict

class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    content_type: str | None
    file_extension: str
    file_size_bytes: int
    status: str
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    message: str
    documents: list[DocumentResponse]