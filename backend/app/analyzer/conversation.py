import re


def parse_conversation(text: str) -> list[dict[str, str | int]]:
    turns: list[dict[str, str | int]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        match = re.match(r"(?:\[(?P<time>[^]]+)\]\s*)?(?P<speaker>[^:]{1,60}):\s*(?P<body>.+)", line)
        if match:
            turns.append({"line": index, "speaker": match.group("speaker").strip(), "text": match.group("body"), "timestamp": match.group("time") or ""})
        else:
            turns.append({"line": index, "speaker": "Unknown", "text": line, "timestamp": ""})
    return turns
