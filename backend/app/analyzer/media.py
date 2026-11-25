from pathlib import Path


AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg", "audio/webm"}
VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}


def inspect_media(filename: str | None, content_type: str | None, size: int, max_bytes: int) -> dict[str, object]:
    suffix = Path(filename or "").suffix.lower()
    kind = "audio" if content_type in AUDIO_TYPES or suffix in {".mp3", ".wav", ".ogg", ".webm"} else "video" if content_type in VIDEO_TYPES or suffix in {".mp4", ".mov"} else "unknown"
    if kind == "unknown" or size > max_bytes:
        raise ValueError("Unsupported or oversized media file.")
    return {"media_type": kind, "filename": Path(filename or "media").name, "size_bytes": size, "status": "metadata-only"}
