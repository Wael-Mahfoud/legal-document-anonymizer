"""Input validation. Only TXT and DOCX are supported in the first release."""

from pathlib import Path

from app.config.settings import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES


class InputValidationError(ValueError):
    """Raised when an uploaded file does not meet input requirements."""


def validate_upload(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise InputValidationError(f"Unsupported file type '{suffix or '(no extension)'}'. Allowed: {allowed}.")
    if not content:
        raise InputValidationError("The uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        size_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        raise InputValidationError(f"The file is too large. The current limit is {size_mb} MiB.")
    if suffix == ".docx" and not content.startswith(b"PK"):
        raise InputValidationError("The file has a .docx extension but does not look like a valid DOCX package.")
    return suffix
