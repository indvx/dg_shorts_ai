from fastapi import FastAPI
from uvicorn import run

from src.api.logs import router as log_router
from src.api.routes import router as api_router

app = FastAPI(title="GoudShorts AI Backend")

app.include_router(log_router)
app.include_router(api_router)