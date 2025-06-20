import re
import zlib
from pathlib import Path


def read_pdf_text(path: str | Path) -> str:
    """Extract text from a PDF file.

    This implementation only handles simple PDFs with optional Flate encoded
    streams. It scans each stream section and tries to decompress it if
    necessary, then collects text within parentheses.
    """
    pdf_path = Path(path)
    data = pdf_path.read_bytes()
    text_parts: list[str] = []

    for match in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        stream_data = match.group(1)
        # remove possible leading newlines
        stream_data = stream_data.strip(b"\r\n")
        # attempt to decompress
        try:
            stream_data = zlib.decompress(stream_data)
        except zlib.error:
            pass
        for section in re.findall(rb"\(([^)]*)\)", stream_data):
            try:
                text_parts.append(section.decode("utf-8"))
            except UnicodeDecodeError:
                text_parts.append(section.decode("latin1", errors="ignore"))
    return "".join(text_parts)
