from pathlib import Path
from app.services.pdf_reader import read_pdf_text


def test_read_pdf_text():
    sample = Path("tests/data/sample.pdf")
    text = read_pdf_text(sample)
    assert "Hello World" in text
