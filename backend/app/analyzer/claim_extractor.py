import re


def extract_claims(statement: str) -> list[str]:
    """Split prose into reviewable claims without asserting their truth."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", statement.strip())
    return [part.strip() for part in parts if part.strip()]
