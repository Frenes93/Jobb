from fastapi import FastAPI
from app.routers import pid

app = FastAPI()


@app.get("/")
async def read_root() -> dict[str, str]:
    """Simple welcome endpoint for the root path."""
    return {"message": "Welcome to the Jobb FastAPI Example"}


app.include_router(pid.router)
