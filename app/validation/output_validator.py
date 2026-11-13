"""Lightweight output validation helpers."""

from io import BytesIO
from docx import Document


def validate_docx_output(content: bytes) -> bool:
    try:
        Document(BytesIO(content))
    except Exception:
        return False
    return True
