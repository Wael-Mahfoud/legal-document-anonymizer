"""DOCX traversal helpers. Paragraph/run structure is preserved for reconstruction."""

from collections.abc import Iterator
from docx.document import Document as DocumentObject
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph


def _iter_element_paragraphs(element, parent, seen: set[int]) -> Iterator[Paragraph]:
    """Walk a Word container in XML order, including paragraphs nested in tables."""
    for block in element.iterchildren():
        if isinstance(block, CT_P):
            paragraph = Paragraph(block, parent)
            key = id(paragraph._p)
            if key not in seen:
                seen.add(key)
                yield paragraph
        elif isinstance(block, CT_Tbl):
            table = Table(block, parent)
            for row in table.rows:
                for cell in row.cells:
                    yield from _iter_element_paragraphs(cell._tc, cell, seen)


def iter_document_paragraphs(document: DocumentObject) -> Iterator[Paragraph]:
    """Yield body paragraphs in document order, then headers and footers once each."""
    seen: set[int] = set()
    yield from _iter_element_paragraphs(document.element.body, document, seen)

    for section in document.sections:
        containers = (
            section.header,
            section.footer,
            section.first_page_header,
            section.first_page_footer,
            section.even_page_header,
            section.even_page_footer,
        )
        for container in containers:
            yield from _iter_element_paragraphs(container._element, container, seen)


def paragraph_text_from_runs(paragraph: Paragraph) -> str:
    """Return exactly the text represented by ordinary paragraph runs."""
    return "".join(run.text for run in paragraph.runs)
