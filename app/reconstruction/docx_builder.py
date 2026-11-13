"""DOCX reconstruction that replaces matched spans in runs instead of resetting paragraph.text."""

from __future__ import annotations

from io import BytesIO
from docx import Document

from app.anonymization.policy import ReplacementPolicy
from app.extraction.docx_extractor import iter_document_paragraphs, paragraph_text_from_runs
from app.pipeline import AnonymizationResult, anonymize_text


def _replace_spans_in_runs(paragraph, entities) -> None:
    runs = list(paragraph.runs)
    original_texts = [run.text for run in runs]
    starts: list[int] = []
    cursor = 0
    for run_text in original_texts:
        starts.append(cursor)
        cursor += len(run_text)

    if not runs or not entities:
        return

    output_by_run: list[str] = []
    for run_index, run_text in enumerate(original_texts):
        run_start = starts[run_index]
        run_end = run_start + len(run_text)
        local_cursor = 0
        pieces: list[str] = []

        for entity in entities:
            if entity.end <= run_start or entity.start >= run_end:
                continue

            overlap_start = max(entity.start, run_start)
            overlap_end = min(entity.end, run_end)
            local_start = overlap_start - run_start
            local_end = overlap_end - run_start
            if local_start < local_cursor:
                continue
            pieces.append(run_text[local_cursor:local_start])

            # Insert the replacement only in the run where the entity begins.
            if run_start <= entity.start < run_end:
                pieces.append(entity.replacement or "")

            local_cursor = max(local_cursor, local_end)

        pieces.append(run_text[local_cursor:])
        output_by_run.append("".join(pieces))

    for run, new_text in zip(runs, output_by_run):
        run.text = new_text


def anonymize_docx_bytes(
    content: bytes,
    selected_types,
    ner_engine=None,
    threshold: float = 0.40,
    policy: ReplacementPolicy | None = None,
) -> tuple[bytes, str, list]:
    document = Document(BytesIO(content))
    active_policy = policy or ReplacementPolicy("redacted")
    preview_paragraphs: list[str] = []
    all_entities = []

    for paragraph in iter_document_paragraphs(document):
        original = paragraph_text_from_runs(paragraph)
        if not original:
            # Empty header/footer and layout paragraphs remain untouched in the file,
            # but are omitted from the simplified preview.
            continue
        result: AnonymizationResult = anonymize_text(
            original,
            selected_types=selected_types,
            ner_engine=ner_engine,
            threshold=threshold,
            policy=active_policy,
        )
        _replace_spans_in_runs(paragraph, result.entities)
        preview_paragraphs.append(result.anonymized_text)
        all_entities.extend(result.entities)

    output = BytesIO()
    document.save(output)
    return output.getvalue(), "\n".join(preview_paragraphs), all_entities
