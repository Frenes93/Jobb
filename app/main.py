from fastapi import FastAPI

from app.routers import pid

app = FastAPI(title="Jobb Example API")

app.include_router(pid.router)
