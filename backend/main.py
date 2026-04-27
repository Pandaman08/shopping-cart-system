import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.connection import init_db
from routers import (
    auth_router,
    cart_router,
    orders_router,
    products_router,
    reports_router,
    statistics_router,
)

load_dotenv()


def _parse_cors_origins() -> list[str]:
    local_defaults = {
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    }

    raw_value = os.getenv(
        "CORS_ORIGINS",
        '["http://localhost:4200", "http://localhost:8501"]',
    )

    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list):
            env_origins = {str(origin) for origin in parsed}
            return sorted(local_defaults | env_origins)
    except json.JSONDecodeError:
        pass

    # Fallback for comma-separated values.
    env_origins = {origin.strip() for origin in raw_value.split(",") if origin.strip()}
    return sorted(local_defaults | env_origins)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Shopping Cart API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(statistics_router)
app.include_router(reports_router)

# Servir archivos estáticos (imágenes)
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/api/images", StaticFiles(directory=str(static_path / "images")), name="images")


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"message": "Shopping Cart API running"}


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
