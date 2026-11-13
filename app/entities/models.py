"""Shared data structures used by NER, rules, and anonymization layers."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Entity:
    """A sensitive span in the original text; end is exclusive."""

    text: str
    label: str
    start: int
    end: int
    score: Optional[float] = None
    source: str = "ner"
    replacement: Optional[str] = None

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValueError("Entity offsets must satisfy 0 <= start <= end.")
