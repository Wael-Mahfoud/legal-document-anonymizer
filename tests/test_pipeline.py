from app.anonymization.policy import ReplacementPolicy
from app.pipeline import anonymize_text


def test_rule_anonymization_preserves_surrounding_text():
    text = "Email jane@example.com today."
    result = anonymize_text(text, {"EMAIL"}, policy=ReplacementPolicy("redacted"))
    assert result.anonymized_text == "Email [REDACTED_EMAIL] today."
    assert len(result.entities) == 1


def test_pseudonym_is_consistent_for_repeated_value():
    policy = ReplacementPolicy("pseudonym")
    text = "jane@example.com and jane@example.com"
    result = anonymize_text(text, {"EMAIL"}, policy=policy)
    assert result.entities[0].replacement == result.entities[1].replacement
    assert result.anonymized_text.count(result.entities[0].replacement) == 2


def test_fake_ner_engine_offsets_are_applied_to_original_text():
    from app.entities.models import Entity

    class FakeNerEngine:
        def detect(self, text, selected_types, threshold=0.4):
            start = text.index("John Smith")
            return [Entity("John Smith", "PER", start, start + len("John Smith"), 0.99, "ner")]

    text = "The employee is John Smith and lives in New York."
    result = anonymize_text(
        text,
        {"PER"},
        ner_engine=FakeNerEngine(),
        policy=ReplacementPolicy("redacted"),
    )
    assert result.anonymized_text == "The employee is [REDACTED_PERSON] and lives in New York."
