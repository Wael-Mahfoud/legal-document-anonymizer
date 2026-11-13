# Legal Document Anonymizer

A first implementation of the Text Obfuscation assignment. It accepts `.txt` and `.docx`, detects selected sensitive entities, replaces them, and returns an anonymized file. The initial domain is English legal documents.

## What works in this version

- TXT and DOCX input (20 MiB limit).
- NuNER Zero / GLiNER for `PER`, `ORG`, and `LOC` (loaded lazily when those categories are selected).
- Local pattern rules for `EMAIL`, `PHONE`, `DATE`, and `ID`.
- Overlap resolution and offset-aware replacement.
- Replacement policies: typed redaction, generic mask, entity type, consistent pseudonyms, and block-character blackout.
- TXT output and DOCX reconstruction. DOCX paragraphs, tables, headers, footers, and standard run formatting are handled by replacing run text instead of assigning `paragraph.text`.
- Streamlit interface and Docker Compose setup.

## Important limitations

This is a coursework prototype, not a guarantee of complete legal or privacy redaction. Model predictions and regular expressions can miss sensitive data or produce false positives. Review each output before sharing it. In DOCX files, content stored in text boxes, hyperlink XML not surfaced as ordinary runs, tracked changes, embedded objects, comments, and unusual field structures are not yet comprehensively handled. PDF and OCR are intentionally postponed.

## Run locally

Use Python 3.11 in a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app/main.py
```

On the first run with `PER`, `ORG`, or `LOC` enabled, NuNER Zero will be downloaded from Hugging Face and cached locally. This model is relatively large; allow sufficient disk space and RAM. The uploaded document is processed locally by the app; model download is the only expected network operation for inference setup.

## Run with Docker

```bash
docker compose up --build
```

Open <http://localhost:8501>. The Hugging Face model cache is stored in a Docker volume so it is not downloaded on every container recreation.

## Run tests

```bash
pytest -q
```

The unit tests do not load the ML model. They verify pattern detection, offset use, replacement, and consistent pseudonyms.

## Pipeline

```text
Upload → Validate → Extract → Chunk with offsets
      ├─ NuNER Zero: PER / ORG / LOC
      └─ Regex rules: EMAIL / PHONE / DATE / ID
      → Resolve overlapping spans → Apply replacement policy
      → Rebuild TXT or DOCX → Validate output → Download
```

## Next milestones

1. Add an annotated legal-document evaluation set and benchmark NER precision/recall/F1.
2. Compare NuNER Zero with a compact pre-trained BERT NER baseline.
3. Improve DOCX support for hyperlinks, text boxes, and more complex Word structures.
4. Add PDF text extraction as the optional next input format.
5. Add a short report with measured results, not estimated performance.
