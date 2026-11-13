"""Project-wide settings for the Text Obfuscation application."""

APP_NAME = "Legal Document Anonymizer"
MODEL_NAME = "numind/NuNERZero"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MiB
ALLOWED_EXTENSIONS = {".txt", ".docx"}
DEFAULT_NER_THRESHOLD = 0.40
MAX_MODEL_CHUNK_CHARS = 1200
MODEL_CHUNK_OVERLAP_CHARS = 100

NER_LABELS = {
    "PER": "person",
    "ORG": "organization",
    "LOC": "location",
}

DISPLAY_LABELS = {
    "PER": "PERSON",
    "ORG": "ORGANIZATION",
    "LOC": "LOCATION",
    "EMAIL": "EMAIL",
    "PHONE": "PHONE",
    "DATE": "DATE",
    "ID": "ID",
}
