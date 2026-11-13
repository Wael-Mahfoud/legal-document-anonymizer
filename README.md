Legal Document Anonymizer

A privacy-focused document anonymization tool built with Python, NuNER Zero, GLiNER, and Streamlit.

Legal Document Anonymizer is a Python-based application designed to detect and anonymize sensitive information in English legal documents. It supports TXT and DOCX files, combining machine-learning-based Named Entity Recognition (NER) with rule-based pattern detection.

The application provides configurable anonymization policies and reconstructs processed documents while preserving standard DOCX formatting.

## Screenshots

### Application Interface
![Application Interface](docs/images/app-interface.png)

### Anonymization Result
![Anonymization Result](docs/images/anonymization-result.png)

### Detection Settings
![Detection Settings](docs/images/original-document.png)

Key Features

- Document Support: Upload and process TXT and DOCX files, with a 20 MiB file-size limit.
- Named Entity Recognition: NuNER Zero / GLiNER detects Person (PER), Organization (ORG), and Location (LOC) entities.
- Rule-Based Detection: Regular expressions identify Email, Phone, Date, and ID patterns.
- Overlap Resolution: Resolves overlapping entity spans before applying replacements.
- Multiple Anonymization Policies:
  - Typed redaction
  - Generic masking
  - Entity-type replacement
  - Consistent pseudonym generation
  - Block-character blackout
- Document Reconstruction: Generates anonymized TXT and DOCX files. DOCX processing supports paragraphs, tables, headers, footers, and standard run formatting.
- Streamlit Interface: Provides a straightforward interface for uploading, processing, and downloading documents.
- Docker Support: Includes Dockerfile and Docker Compose configuration for containerized deployment.

Technology Stack

Component| Technology
Programming Language| Python 3.11
NER Model| NuNER Zero
NER Framework| GLiNER
Pattern Detection| Regular Expressions
Document Processing| python-docx
User Interface| Streamlit
Containerization| Docker & Docker Compose
Testing| pytest

## System Architecture

The following diagram illustrates the overall architecture and
processing workflow of the Legal Document Anonymizer, from
document upload and entity detection to anonymization and
document reconstruction.

flowchart TD
    A["User"] --> B["Streamlit Web Interface"]
    B --> C["File Validation"]
    C --> D["Document Loader"]
    D --> E{"File Type"}
    E -->|TXT| F["TXT Extractor"]
    E -->|DOCX| G["DOCX Extractor"]
    F --> H["Text Normalization & Chunking"]
    G --> H
    H --> I["Entity Detection"]
    I --> J["NuNER Zero / GLiNER"]
    I --> K["Regex Pattern Detector"]
    J --> L["Entity Resolver"]
    K --> L
    L --> M["Replacement Policy"]
    M --> N["Document Reconstruction"]
    N --> O["Output Validation"]
    O --> P["Download Anonymized Document"]

Anonymization Strategies

The application supports different replacement strategies depending on the required anonymization policy:

Strategy| Description
Typed Redaction| Replaces sensitive content with a descriptive redaction marker.
Generic Mask| Replaces detected values with a generic mask.
Entity Type| Uses the detected entity category as the replacement.
Consistent Pseudonyms| Assigns consistent fake values to repeated entities.
Blackout| Replaces sensitive content with block characters.

Getting Started

Prerequisites

- Python 3.11 for local installation.
- Docker and Docker Compose for containerized execution.
- Sufficient disk space and RAM for loading the NuNER Zero model.

Run Locally

Create and activate a virtual environment:

python -m venv .venv

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

macOS / Linux:

source .venv/bin/activate

Install dependencies:

python -m pip install --upgrade pip
pip install -r requirements.txt

Start the application:

streamlit run app/main.py

On the first run, when PER, ORG, or LOC detection is enabled, NuNER Zero may need to be downloaded from Hugging Face. The model is cached locally for subsequent runs.

Run with Docker

Build and start the application:

docker compose up --build

Open the application at:

http://localhost:8501

The Hugging Face model cache is stored in a Docker volume to avoid downloading the model again whenever the container is recreated.

Testing

Run the automated test suite:

pytest -q

The current unit tests cover:
- Pattern detection.
- Entity span and offset handling.
- Overlapping entity resolution.
- Replacement policies.
- Consistent pseudonym generation.
- Document reconstruction.

The unit tests do not load the machine learning model or constitute a complete evaluation of NER accuracy.

Security and Privacy Considerations

This project is designed to process documents locally when running in a local or self-hosted environment.

Important considerations:

- Model downloads require an internet connection during initial setup unless the model is already cached.
- Uploaded documents should be handled securely.
- Anonymized outputs must be reviewed before being shared.
- The application does not guarantee complete removal of all sensitive information.

Do not use this coursework prototype as the sole protection mechanism for confidential legal or personal documents.

Current Limitations

This is an initial coursework implementation, not a production-grade anonymization system.

Known limitations include:

- NER predictions and regular expressions may produce false positives or miss sensitive information.
- DOCX text boxes, hyperlink XML not exposed as ordinary runs, tracked changes, embedded objects, comments, and unusual Word field structures are not comprehensively supported.
- PDF extraction and OCR are not currently implemented.
- The initial target domain is English legal documents.

Roadmap

1. Build an annotated legal-document evaluation dataset.
2. Benchmark NER performance using Precision, Recall, and F1-score.
3. Compare NuNER Zero with a compact pre-trained BERT-based NER model.
4. Improve DOCX support for hyperlinks, text boxes, and complex Word structures.
5. Introduce PDF text extraction as an additional input format.
6. Publish a technical evaluation report based on measured results.

Project Status

<em>Initial implementation – under development.</em>

Future releases will focus on improving detection accuracy, document compatibility, and evaluation reliability.

Author

Wael Mahfoud

Software Engineer | Information Engineering

- GitHub: "Wael-Mahfoud" (https://github.com/Wael-Mahfoud)
