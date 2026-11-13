"""Rule-based detection for sensitive values that are not reliably covered by NER."""

import re
from collections.abc import Iterable

from app.entities.models import Entity

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
DATE_PATTERNS = (
    re.compile(
        r"(?i)\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
        r"sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?[,]?\s+\d{4}\b"
    ),
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
)
PHONE_RE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{6,}\d(?!\w)")
LABELED_ID_RE = re.compile(
    r"(?i)\b(?:tax\s+id|ssn|passport|license|registration\s+no\.?|employee\s+id|account\s+no\.?)"
    r"\s*(?:number|no\.?|#|:)?\s*[:#-]?\s*[A-Z0-9][A-Z0-9-]{4,}\b"
)
GENERIC_ID_RE = re.compile(r"\b[A-Z]{2,5}[-]?[0-9]{6,}\b")


def _matches(pattern: re.Pattern[str], text: str, label: str) -> list[Entity]:
    return [
        Entity(text=match.group(0), label=label, start=match.start(), end=match.end(), score=1.0, source="rule")
        for match in pattern.finditer(text)
    ]


def detect_pattern_entities(text: str, selected_types: Iterable[str]) -> list[Entity]:
    selected = set(selected_types)
    results: list[Entity] = []

    if "EMAIL" in selected:
        results.extend(_matches(EMAIL_RE, text, "EMAIL"))

    date_matches: list[Entity] = []
    if "DATE" in selected:
        for pattern in DATE_PATTERNS:
            date_matches.extend(_matches(pattern, text, "DATE"))
        results.extend(date_matches)

    if "PHONE" in selected:
        for entity in _matches(PHONE_RE, text, "PHONE"):
            digits = sum(character.isdigit() for character in entity.text)
            # Avoid treating date strings or short numeric values as telephone numbers.
            overlaps_date = any(entity.start < date.end and date.start < entity.end for date in date_matches)
            if 9 <= digits <= 15 and not overlaps_date:
                results.append(entity)

    if "ID" in selected:
        results.extend(_matches(LABELED_ID_RE, text, "ID"))
        results.extend(_matches(GENERIC_ID_RE, text, "ID"))

    return results
