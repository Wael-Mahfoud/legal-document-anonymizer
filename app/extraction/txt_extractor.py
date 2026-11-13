"""Text file extraction."""


def decode_text(content: bytes) -> str:
    """Decode common text encodings without silently dropping characters."""
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode the text file. Please save it as UTF-8 and retry.")


def encode_text(text: str) -> bytes:
    return text.encode("utf-8")
