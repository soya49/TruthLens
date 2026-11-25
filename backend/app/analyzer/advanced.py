import re
from collections import Counter


def semantic_observations(text: str) -> list[str]:
    observations: list[str] = []
    if re.search(r"\b(because|therefore|so that)\b", text, re.IGNORECASE):
        observations.append("Contains an explicit causal connection; check whether the stated cause is independently supported.")
    if re.search(r"\b(I think|I believe|as far as I remember|to my knowledge)\b", text, re.IGNORECASE):
        observations.append("Uses a memory or belief qualifier; distinguish recollection from directly observed fact.")
    return observations


def compare_word_usage(statements: list[str]) -> list[str]:
    if len(statements) < 2:
        return []
    vocab = [set(re.findall(r"[A-Za-z]{4,}", item.lower())) for item in statements]
    repeated = Counter(word for group in vocab for word in group)
    changed = [word for word, count in repeated.items() if count == 1]
    return [f"Some content words occur in only one version: {', '.join(sorted(changed)[:8])}."] if changed else []
