import io
from PyPDF2 import PdfReader
from docx import Document


def extract_text(content: bytes, filename: str) -> str:
    """
    Extract text from file content based on file type.

    Args:
        content: The raw bytes of the file
        filename: The name of the file (used to determine file type)

    Returns:
        Extracted text as a string

    Raises:
        ValueError: If text extraction fails
    """
    filename_lower = filename.lower()

    try:
        if filename_lower.endswith(".pdf"):
            return _extract_pdf(content)
        elif filename_lower.endswith(".docx"):
            return _extract_docx(content)
        else:
            # Fallback: try to decode as UTF-8 text
            return content.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to extract text from {filename}: {str(e)}")


def _extract_pdf(content: bytes) -> str:
    """Extract text from PDF content."""
    pdf_file = io.BytesIO(content)
    reader = PdfReader(pdf_file)

    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return "\n".join(text_parts)


def _extract_docx(content: bytes) -> str:
    """Extract text from DOCX content."""
    docx_file = io.BytesIO(content)
    document = Document(docx_file)

    text_parts = []
    for paragraph in document.paragraphs:
        if paragraph.text:
            text_parts.append(paragraph.text)

    return "\n".join(text_parts)
