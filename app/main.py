from fastapi import FastAPI
from app.routers import pid

app = FastAPI()
app.include_router(pid.router)
