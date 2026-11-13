# Text Obfuscation Project — Short Report (Draft Template)

## 1. Chosen domain and model

The prototype targets English legal documents such as employment agreements and service contracts. The initial NER engine is NuNER Zero through GLiNER, with the labels person, organization, and location mapped to PER, ORG, and LOC. Regular-expression rules separately detect email addresses, phone numbers, dates, and selected labeled identifiers. The final model choice must be confirmed after evaluating both false positives and false negatives on a small annotated set.

## 2. System architecture

The pipeline is: input validation → text extraction → offset-preserving chunking → NER and rule-based detection → overlap resolution → anonymization policy → text replacement → document reconstruction → output validation. TXT input is returned as UTF-8 text. DOCX reconstruction edits run text rather than replacing entire paragraphs, which helps preserve unaffected text and common run formatting.

## 3. Replacement methods

The application supports typed redaction (`[REDACTED_PERSON]`), generic masking (`*****`), entity-type replacement (`[PERSON]`), consistent pseudonyms via Faker, and block-character replacement. The original sensitive span is replaced in the output; visual block characters are not an overlay hiding original text.

## 4. Challenges and current limitations

Entity offsets must stay aligned with the original text, particularly when a name spans multiple Word runs. The model can miss entities, and regex rules may produce false positives. Complex DOCX constructs such as text boxes, tracked changes, and some hyperlink structures require additional handling. PDF and OCR are outside this initial version.

## 5. Evaluation (fill after experiments)

- Dataset and annotation procedure: [to be completed]
- NuNER Zero precision / recall / F1: [measure]
- BERT baseline precision / recall / F1: [measure]
- Mean processing time and hardware: [measure]
- Before/after examples: [insert examples]
- Known errors and mitigations: [describe observed errors]
