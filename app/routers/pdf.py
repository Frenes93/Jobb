from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.services.pdf_reader import read_pdf_text

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.get("/read")
async def read_pdf(path: str) -> dict[str, str]:
    """Return extracted text from the given PDF file path."""
    pdf_path = Path(path)
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    text = read_pdf_text(pdf_path)
    return {"text": text}
