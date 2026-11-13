from app.rules.pattern_detector import detect_pattern_entities


def test_email_and_date_detection():
    text = "Contact jane.doe@example.com before January 15, 2025."
    entities = detect_pattern_entities(text, {"EMAIL", "DATE"})
    assert [(e.label, e.text) for e in entities] == [
        ("EMAIL", "jane.doe@example.com"),
        ("DATE", "January 15, 2025"),
    ]
    for entity in entities:
        assert text[entity.start:entity.end] == entity.text


def test_phone_detection_does_not_treat_date_as_phone():
    text = "Call +1 (212) 555-0198 on 01/15/2025."
    entities = detect_pattern_entities(text, {"PHONE", "DATE"})
    assert any(e.label == "PHONE" for e in entities)
    assert any(e.label == "DATE" for e in entities)
    assert all(not (e.label == "PHONE" and "/" in e.text) for e in entities)


def test_id_detection():
    text = "The Employee ID is EMP-12345678."
    entities = detect_pattern_entities(text, {"ID"})
    assert any(e.label == "ID" and "EMP-12345678" in e.text for e in entities)
