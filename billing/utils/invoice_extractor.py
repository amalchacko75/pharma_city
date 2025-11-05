import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import re
import tempfile


def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image using Tesseract OCR."""
    return pytesseract.image_to_string(Image.open(image_path))


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a machine-generated PDF."""
    reader = PdfReader(pdf_path)
    return " ".join([page.extract_text() or "" for page in reader.pages])


def extract_drug_names(text: str) -> list[str]:
    """
    Extract potential drug/product names from invoice text.
    Uses regex and cleanup filters.
    """
    # Clean up text
    text = re.sub(r"[^A-Za-z0-9+\-\s()]", " ", text)
    text = re.sub(r"\s+", " ", text)

    # Split by common separators
    lines = re.split(r"\d+\s+|\n|\\n|\r", text)
    potential_drugs = []

    for line in lines:
        line = line.strip()
        # Skip junk lines
        if not line or len(line) < 3:
            continue
        # Filter probable product/drug lines
        if re.search(r"[A-Za-z]", line) and len(line.split()) <= 6:
            if not any(word.lower() in line.lower() for word in [
                # "gst", "invoice", "amount", "total",
                # "rate",
                "item", "item name", "item description"
            ]):
                potential_drugs.append(line)

    # Remove duplicates and sort
    return sorted(set(potential_drugs))


def extract_invoice_drugs(file) -> list[str]:
    """Auto-detect file type and extract drug names."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    try:
        if tmp_path.lower().endswith(".pdf"):
            text = extract_text_from_pdf(tmp_path)
        else:
            text = extract_text_from_image(tmp_path)
    except Exception as e:
        raise RuntimeError(f"OCR extraction failed: {e}")

    return extract_drug_names(text)
