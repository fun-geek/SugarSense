
from pathlib import Path

from config.settings import (
    ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE_MB,
)


def validate_report(filename: str, file_bytes: bytes) -> None:
    """Validate an uploaded report before processing."""

    if not filename or not filename.strip():
        raise ValueError("Please select a file.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Upload a PDF, PNG, JPG, or JPEG."
        )

    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(file_bytes) > max_size_bytes:
        raise ValueError(
            f"File size must not exceed {MAX_UPLOAD_SIZE_MB} MB."
        )

    # Check basic file signatures, not just the filename.
    if extension == ".pdf":
        valid_signature = file_bytes.startswith(b"%PDF-")
    elif extension == ".png":
        valid_signature = file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    elif extension in {".jpg", ".jpeg"}:
        valid_signature = file_bytes.startswith(b"\xff\xd8\xff")
    else:
        valid_signature = False

    if not valid_signature:
        raise ValueError(
            "The file content does not match its extension."
        )
