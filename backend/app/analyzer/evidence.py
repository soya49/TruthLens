from pathlib import Path


ALLOWED_TYPES = {"text/plain", "application/pdf", "image/png", "image/jpeg"}
ALLOWED_SUFFIXES = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}


def validate_upload(filename: str | None, content_type: str | None, size: int, max_bytes: int) -> None:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES or content_type not in ALLOWED_TYPES:
        raise ValueError("Only TXT, PDF, PNG, and JPEG evidence files are supported.")
    if size > max_bytes:
        raise ValueError("Evidence file exceeds the configured size limit.")


def extract_text(filename: str, content_type: str | None, content: bytes) -> tuple[str, str]:
    if content_type == "text/plain" or filename.lower().endswith(".txt"):
        return content.decode("utf-8", errors="replace"), "text-extraction"
    return "", "metadata-only"
