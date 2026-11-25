import re


def build_timeline(text: str) -> list[dict[str, str | int]]:
    events = []
    for index, sentence in enumerate(re.split(r"(?<=[.!?])\s+|\n+", text.strip()), start=1):
        if not sentence.strip():
            continue
        temporal = re.findall(r"\b(?:\d{1,2}:\d{2}|\d{1,2}\s?(?:am|pm)|\d{4}-\d{2}-\d{2}|\b(?:yesterday|today|tomorrow|morning|evening)\b)", sentence, re.IGNORECASE)
        events.append({"order": index, "description": sentence.strip(), "temporal_references": temporal})
    return events
