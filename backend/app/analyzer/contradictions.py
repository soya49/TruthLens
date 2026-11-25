import re


_NUMBER = re.compile(r"\b\d+(?:[.:/]\d+)?\b")


def compare_claims(current: list[str], previous: list[str]) -> list[tuple[str, str]]:
    """Return only explicit, reviewable conflicts; semantic uncertainty is not a contradiction."""
    findings: list[tuple[str, str]] = []
    previous_text = " ".join(previous)
    for claim in current:
        numbers = set(_NUMBER.findall(claim))
        if not numbers:
            continue
        for old in previous:
            old_numbers = set(_NUMBER.findall(old))
            if old_numbers and numbers.isdisjoint(old_numbers):
                findings.append((claim, old))
                break
    return findings
