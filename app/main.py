from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers import pid, pdf, fittings

app = FastAPI()

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def frontend() -> FileResponse:
    """Serve the HTML frontend for the application."""
    return FileResponse(static_dir / "index.html")


@app.get("/upload")
async def upload_portal() -> FileResponse:
    """Serve the PDF upload portal."""
    return FileResponse(static_dir / "upload.html")


@app.get("/api")
async def read_root() -> dict[str, str]:
    """Simple welcome endpoint for the API root path."""
    return {"message": "Welcome to the Jobb FastAPI Example"}


app.include_router(pid.router)
app.include_router(pdf.router)
app.include_router(fittings.router)
