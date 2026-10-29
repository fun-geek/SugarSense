
from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract selectable text from a digital PDF."""

    try:
        reader = PdfReader(BytesIO(file_bytes), strict=True)

        if reader.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported yet."
            )

        if len(reader.pages) == 0:
            raise ValueError("The PDF contains no pages.")

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                extracted_pages.append(
                    f"\n--- Page {page_number} ---\n{text}"
                )

        return "\n".join(extracted_pages).strip()

    except ValueError:
        raise
    except Exception as error:
        raise ValueError(
            "Unable to read this PDF. Check that it is a valid PDF."
        ) from error
