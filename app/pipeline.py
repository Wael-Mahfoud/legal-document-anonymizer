"""Orchestration for detection, conflict resolution, and text anonymization."""

from dataclasses import dataclass
from collections.abc import Iterable

from app.anonymization.policy import ReplacementPolicy
from app.config.settings import DEFAULT_NER_THRESHOLD
from app.entities.models import Entity
from app.entities.resolver import resolve_overlaps
from app.normalization.chunker import iter_chunks_with_offsets
from app.rules.pattern_detector import detect_pattern_entities


@dataclass
class AnonymizationResult:
    original_text: str
    anonymized_text: str
    entities: list[Entity]


def detect_entities(
    text: str,
    selected_types: Iterable[str],
    ner_engine=None,
    threshold: float = DEFAULT_NER_THRESHOLD,
) -> list[Entity]:
    selected = set(selected_types)
    candidates = detect_pattern_entities(text, selected)
    ner_types = selected.intersection({"PER", "ORG", "LOC"})

    if ner_types and ner_engine is not None:
        for absolute_start, chunk in iter_chunks_with_offsets(text):
            if not chunk.strip():
                continue
            for entity in ner_engine.detect(chunk, ner_types, threshold=threshold):
                entity.start += absolute_start
                entity.end += absolute_start
                candidates.append(entity)

    return resolve_overlaps(candidates, text)


def anonymize_text(
    text: str,
    selected_types: Iterable[str],
    ner_engine=None,
    threshold: float = DEFAULT_NER_THRESHOLD,
    policy: ReplacementPolicy | None = None,
) -> AnonymizationResult:
    active_policy = policy or ReplacementPolicy("redacted")
    entities = detect_entities(text, selected_types, ner_engine=ner_engine, threshold=threshold)

    for entity in entities:
        entity.replacement = active_policy.replacement_for(entity)

    anonymized = text
    # Replace from right to left so the original offsets remain valid.
    for entity in reversed(entities):
        anonymized = anonymized[:entity.start] + (entity.replacement or "") + anonymized[entity.end:]

    return AnonymizationResult(original_text=text, anonymized_text=anonymized, entities=entities)
