import re


def inspect_language(claim: str) -> list[str]:
    observations: list[str] = []
    if re.search(r"\b(always|never|everyone|no one)\b", claim, re.IGNORECASE):
        observations.append("Contains an absolute quantifier; its scope may need clarification.")
    if re.search(r"\b(somehow|something|somewhere|around|maybe|probably)\b", claim, re.IGNORECASE):
        observations.append("Contains a vague expression that may reduce verifiability.")
    if len(claim.split()) > 45:
        observations.append("Long sentence; separate events or time references may be worth checking.")
    return observations
