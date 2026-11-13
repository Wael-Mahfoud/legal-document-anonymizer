"""Replacement policy with consistent pseudonyms for repeated entities."""

from __future__ import annotations

import re
from faker import Faker

from app.config.settings import DISPLAY_LABELS
from app.entities.models import Entity


class ReplacementPolicy:
    METHODS = {
        "redacted": "Typed redaction",
        "mask": "Generic mask",
        "entity_type": "Entity type",
        "pseudonym": "Consistent pseudonym",
        "blackout": "Blackout blocks",
    }

    def __init__(self, method: str = "redacted", locale: str = "en_US") -> None:
        if method not in self.METHODS:
            raise ValueError(f"Unknown anonymization method: {method}")
        self.method = method
        self.fake = Faker(locale)
        self.mapping: dict[tuple[str, str], str] = {}

    def replacement_for(self, entity: Entity) -> str:
        normalized = re.sub(r"\s+", " ", entity.text).strip().casefold()
        key = (entity.label, normalized)

        if self.method == "redacted":
            return f"[REDACTED_{DISPLAY_LABELS.get(entity.label, entity.label)}]"
        if self.method == "mask":
            return "*****"
        if self.method == "entity_type":
            return f"[{DISPLAY_LABELS.get(entity.label, entity.label)}]"
        if self.method == "blackout":
            return "█" * max(4, min(len(entity.text), 24))

        if key not in self.mapping:
            self.mapping[key] = self._make_pseudonym(entity.label)
        return self.mapping[key]

    def _make_pseudonym(self, label: str) -> str:
        if label == "PER":
            return self.fake.name()
        if label == "ORG":
            return self.fake.company()
        if label == "LOC":
            return self.fake.city()
        if label == "EMAIL":
            return self.fake.safe_email()
        if label == "PHONE":
            return self.fake.phone_number()
        if label == "DATE":
            return self.fake.date(pattern="%B %d, %Y")
        if label == "ID":
            return self.fake.bothify(text="??-########").upper()
        return "[REDACTED]"
