class DocumentError(Exception):
    """Base exception for document-related errors."""


class DocumentUploadError(DocumentError):
    """Raised when document upload fails."""


class UnsupportedDocumentTypeError(DocumentUploadError):
    """Raised when the uploaded file type is not supported."""


class DocumentTooLargeError(DocumentUploadError):
    """Raised when the uploaded document exceeds the max allowed size."""


class EmptyDocumentError(DocumentUploadError):
    """Raised when the uploaded document has no extractable text."""


class DocumentTextExtractionError(DocumentUploadError):
    """Raised when text extraction fails."""


class DocumentNotFoundError(DocumentError):
    """Raised when a document cannot be found."""