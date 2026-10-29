
from pathlib import Path
from uuid import uuid4

from config.settings import PRIVATE_REPORTS_DIR
from database.repository import add_report

from report_processing.validators import validate_report
from report_processing.pdf_extractor import extract_pdf_text
from report_processing.value_extractor import extract_candidates


# ==================================================
# PROCESS MEDICAL REPORT
# ==================================================

def process_report(filename: str, file_bytes: bytes) -> dict:
    """
    Validate a report, extract selectable PDF text,
    and identify candidate measurements.

    OCR is not required for this version.
    """

    validate_report(filename, file_bytes)

    extension = Path(filename).suffix.lower()

    if extension != ".pdf":
        raise ValueError(
            "Image OCR is not configured yet. For now, upload "
            "a PDF containing selectable text."
        )

    text = extract_pdf_text(file_bytes)

    if not text.strip():
        raise ValueError(
            "No selectable text was found. This may be a scanned PDF. "
            "OCR can be enabled later."
        )

    candidates = extract_candidates(text)

    return {
        "filename": Path(filename).name,
        "file_type": "pdf",
        "extraction_method": "pdf_text",
        "text": text,
        "candidates": candidates,
    }


# ==================================================
# STORE REPORT FILE AND DATABASE METADATA
# ==================================================

def store_report_file(filename: str, file_bytes: bytes) -> int:
    """
    Store a PDF locally and create its database record.

    Returns the report ID.
    """

    safe_original_filename = Path(filename).name

    if not safe_original_filename:
        raise ValueError("Invalid report filename.")

    extension = Path(safe_original_filename).suffix.lower()

    if extension != ".pdf":
        raise ValueError("Only PDF reports are supported currently.")

    # Validate the uploaded file before storing it.
    validate_report(safe_original_filename, file_bytes)

    if not file_bytes.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    PRIVATE_REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Use a unique filename to prevent overwriting existing reports.
    stored_filename = f"{uuid4().hex}.pdf"
    destination = PRIVATE_REPORTS_DIR / stored_filename

    # Save the file first.
    with destination.open("xb") as report_file:
        report_file.write(file_bytes)

    try:
        # Save metadata in SQLite.
        report_id = add_report(
            original_filename=safe_original_filename,
            stored_filename=stored_filename,
            file_type="pdf",
            processing_status="processed",
        )

        return report_id

    except Exception:
        # If metadata insertion fails, remove the untracked file.
        destination.unlink(missing_ok=True)
        raise
