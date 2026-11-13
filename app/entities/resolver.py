"""Deduplicate overlapping detections from the model and rule engine."""

from collections.abc import Iterable

from app.entities.models import Entity


def resolve_overlaps(entities: Iterable[Entity], text: str) -> list[Entity]:
    candidates = [
        entity for entity in entities
        if 0 <= entity.start < entity.end <= len(text) and text[entity.start:entity.end]
    ]
    # Sort so overlapping spans form contiguous groups. Prefer the longest span in each group,
    # then deterministic rule matches, then model confidence.
    candidates.sort(key=lambda e: (e.start, e.end))
    groups: list[list[Entity]] = []
    current: list[Entity] = []
    current_end = -1
    for entity in candidates:
        if not current or entity.start < current_end:
            current.append(entity)
            current_end = max(current_end, entity.end)
        else:
            groups.append(current)
            current = [entity]
            current_end = entity.end
    if current:
        groups.append(current)

    resolved: list[Entity] = []
    for group in groups:
        # Exact duplicate spans are reduced to one label. Longer matches win for partial overlaps.
        winner = max(
            group,
            key=lambda e: (
                e.end - e.start,
                1 if e.source == "rule" else 0,
                e.score if e.score is not None else 0.0,
            ),
        )
        resolved.append(winner)

    resolved.sort(key=lambda e: (e.start, e.end))
    return resolved
