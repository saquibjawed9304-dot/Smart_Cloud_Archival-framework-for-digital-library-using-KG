import re


def extract_entities(text: str):
    entities = []

    if not text:
        return entities

    # Basic person detection based on common title patterns.
    person_patterns = re.findall(
        r"\b(?:Dr\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*",
        text
    )

    for person in person_patterns:
        entities.append({
            "text": person,
            "type": "Person"
        })

    # Detect common institution terms.
    institution_patterns = re.findall(
        r"\b[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)*\s+(?:University|Institute)\b",
        text
    )

    for institution in institution_patterns:
        entities.append({
            "text": institution,
            "type": "Institution"
        })

    return entities