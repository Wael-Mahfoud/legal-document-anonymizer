"""Streamlit user interface for the Legal Document Anonymizer."""

from pathlib import Path
import pandas as pd
import streamlit as st

from app.anonymization.policy import ReplacementPolicy
from app.config.settings import APP_NAME, DEFAULT_NER_THRESHOLD, MAX_UPLOAD_BYTES
from app.extraction.txt_extractor import decode_text, encode_text
from app.ingestion.validator import InputValidationError, validate_upload
from app.ner.nuner_engine import NuNerEngine
from app.pipeline import anonymize_text
from app.reconstruction.docx_builder import anonymize_docx_bytes
from app.validation.output_validator import validate_docx_output

st.set_page_config(page_title=APP_NAME, page_icon="🔒", layout="wide")


@st.cache_resource(show_spinner=False)
def get_ner_engine() -> NuNerEngine:
    return NuNerEngine()


def entity_label(label: str) -> str:
    return {
        "PER": "Person",
        "ORG": "Organization",
        "LOC": "Location",
        "EMAIL": "Email",
        "PHONE": "Phone",
        "DATE": "Date",
        "ID": "ID / reference number",
    }.get(label, label)


st.title("🔒 Legal Document Anonymizer")
st.caption("A local-first prototype for identifying and anonymizing sensitive data in English legal documents.")

with st.sidebar:
    st.header("Detection settings")
    entity_choices = {
        "Person (PER)": "PER",
        "Organization (ORG)": "ORG",
        "Location (LOC)": "LOC",
        "Email address": "EMAIL",
        "Phone number": "PHONE",
        "Date": "DATE",
        "ID / reference number": "ID",
    }
    chosen_labels = st.multiselect(
        "Sensitive categories",
        options=list(entity_choices.keys()),
        default=["Person (PER)", "Organization (ORG)", "Location (LOC)"],
        help="PER/ORG/LOC use NuNER Zero. Email/phone/date/ID use local pattern rules.",
    )
    selected_types = {entity_choices[label] for label in chosen_labels}
    threshold = st.slider(
        "NER confidence threshold",
        min_value=0.10,
        max_value=0.90,
        value=float(DEFAULT_NER_THRESHOLD),
        step=0.05,
        help="Higher values may reduce false positives but can miss names.",
    )
    replacement_options = {
        "Typed redaction — [REDACTED_PERSON]": "redacted",
        "Generic mask — *****": "mask",
        "Entity type — [PERSON]": "entity_type",
        "Consistent pseudonyms": "pseudonym",
        "Blackout blocks — █████": "blackout",
    }
    replacement_label = st.selectbox("Replacement method", list(replacement_options.keys()))
    replacement_method = replacement_options[replacement_label]

st.info(
    "Privacy note: document text is processed locally by this application. On the first run, the selected model is downloaded from Hugging Face; "
    "the uploaded document itself is not sent to the model publisher. This prototype does not yet support PDF."
)

uploaded = st.file_uploader(
    "Upload a legal document (.docx or .txt)",
    type=["docx", "txt"],
    accept_multiple_files=False,
)

if uploaded is not None:
    raw_bytes = uploaded.getvalue()
    st.caption(f"File: {uploaded.name} · Size: {len(raw_bytes) / 1024:.1f} KiB")

    if st.button("Anonymize document", type="primary", use_container_width=True):
        try:
            suffix = validate_upload(uploaded.name, raw_bytes)
            policy = ReplacementPolicy(replacement_method)
            needs_ner = bool(selected_types.intersection({"PER", "ORG", "LOC"}))
            engine = get_ner_engine() if needs_ner else None

            with st.spinner("Analyzing text and anonymizing selected entities..."):
                if suffix == ".txt":
                    original = decode_text(raw_bytes)
                    result = anonymize_text(
                        original,
                        selected_types=selected_types,
                        ner_engine=engine,
                        threshold=threshold,
                        policy=policy,
                    )
                    output_bytes = encode_text(result.anonymized_text)
                    preview_text = result.anonymized_text
                    entities = result.entities
                    output_name = f"{Path(uploaded.name).stem}_anonymized.txt"
                    output_mime = "text/plain; charset=utf-8"
                else:
                    output_bytes, preview_text, entities = anonymize_docx_bytes(
                        raw_bytes,
                        selected_types=selected_types,
                        ner_engine=engine,
                        threshold=threshold,
                        policy=policy,
                    )
                    if not validate_docx_output(output_bytes):
                        raise RuntimeError("The rebuilt DOCX did not pass validation.")
                    output_name = f"{Path(uploaded.name).stem}_anonymized.docx"
                    output_mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            st.session_state["anonymize_result"] = {
                "preview": preview_text,
                "output_bytes": output_bytes,
                "output_name": output_name,
                "output_mime": output_mime,
                "entities": entities,
                "source_name": uploaded.name,
            }
        except (InputValidationError, UnicodeError, ValueError, RuntimeError) as exc:
            st.error(str(exc))
        except Exception as exc:  # Keep unexpected implementation errors visible but contained in the UI.
            st.exception(exc)

if "anonymize_result" in st.session_state:
    result_data = st.session_state["anonymize_result"]
    if result_data["source_name"] == (uploaded.name if uploaded is not None else None):
        st.success(f"Completed. Detected and handled {len(result_data['entities'])} entity/ies.")
        left, right = st.columns(2)
        with left:
            st.subheader("Anonymized text preview")
            st.text_area("Preview", result_data["preview"], height=360, label_visibility="collapsed")
        with right:
            st.subheader("Detected entities")
            entities = result_data["entities"]
            if entities:
                frame = pd.DataFrame(
                    [
                        {
                            "Type": entity_label(entity.label),
                            "Original value": entity.text,
                            "Replacement": entity.replacement,
                            "Detected by": entity.source,
                            "Score": round(entity.score, 3) if entity.score is not None else None,
                        }
                        for entity in entities
                    ]
                )
                st.dataframe(frame, use_container_width=True, hide_index=True)
            else:
                st.write("No selected entities were detected. This does not guarantee that the document contains no sensitive data.")
        st.download_button(
            "Download anonymized document",
            data=result_data["output_bytes"],
            file_name=result_data["output_name"],
            mime=result_data["output_mime"],
            use_container_width=True,
        )

st.divider()
st.caption(
    f"Prototype limits: maximum upload {MAX_UPLOAD_BYTES // (1024 * 1024)} MiB; English legal documents; PDF, OCR, "
    "hyperlink text boxes, tracked changes, and password-protected files are not in scope for this first release. Review outputs before use."
)
