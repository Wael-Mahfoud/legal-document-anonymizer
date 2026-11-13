from io import BytesIO

from docx import Document

from app.anonymization.policy import ReplacementPolicy
from app.extraction.docx_extractor import paragraph_text_from_runs
from app.reconstruction.docx_builder import anonymize_docx_bytes


def test_docx_reconstruction_replaces_entity_across_runs_and_opens():
    source = Document()
    paragraph = source.add_paragraph()
    paragraph.add_run("Contact jane.")
    paragraph.add_run("doe@example.com today.").bold = True
    original = BytesIO()
    source.save(original)

    result_bytes, preview, entities = anonymize_docx_bytes(
        original.getvalue(),
        selected_types={"EMAIL"},
        ner_engine=None,
        policy=ReplacementPolicy("redacted"),
    )

    rebuilt = Document(BytesIO(result_bytes))
    rebuilt_text = paragraph_text_from_runs(rebuilt.paragraphs[0])
    assert rebuilt_text == "Contact [REDACTED_EMAIL] today."
    assert preview == rebuilt_text
    assert len(entities) == 1
    assert entities[0].text == "jane.doe@example.com"
    # The replacement run keeps the style of the run where the email began;
    # unaffected trailing text remains in the original second run and style.
    assert rebuilt.paragraphs[0].runs[-1].bold is True


def test_docx_table_cells_are_processed_in_document_order():
    source = Document()
    source.add_paragraph("Opening contact: first@example.com")
    table = source.add_table(rows=1, cols=1)
    table.cell(0, 0).text = "Table contact: second@example.com"
    source.add_paragraph("Closing contact: third@example.com")
    original = BytesIO()
    source.save(original)

    result_bytes, preview, entities = anonymize_docx_bytes(
        original.getvalue(),
        selected_types={"EMAIL"},
        ner_engine=None,
        policy=ReplacementPolicy("redacted"),
    )

    rebuilt = Document(BytesIO(result_bytes))
    body_text = []
    for paragraph in rebuilt.paragraphs:
        if paragraph_text_from_runs(paragraph):
            body_text.append(paragraph_text_from_runs(paragraph))
    for row in rebuilt.tables[0].rows:
        for cell in row.cells:
            body_text.extend(paragraph_text_from_runs(p) for p in cell.paragraphs if paragraph_text_from_runs(p))
    assert len(entities) == 3
    assert "[REDACTED_EMAIL]" in preview
    assert "first@example.com" not in preview
    assert "second@example.com" not in preview
    assert "third@example.com" not in preview
    assert "Table contact: [REDACTED_EMAIL]" in preview
