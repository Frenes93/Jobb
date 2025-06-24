from fastapi import FastAPI

from app.routers import pid, pdf, fittings

app = FastAPI()


@app.get("/")
async def frontend() -> dict[str, str]:
    """Root endpoint providing a simple welcome message."""
    return {"message": "Welcome to the Jobb API"}


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
