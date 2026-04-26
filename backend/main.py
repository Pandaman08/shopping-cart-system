import json
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    raw_value = os.getenv(
        "CORS_ORIGINS",
        '["http://localhost:4200", "http://localhost:8501"]',
    )

    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, list):
            return [str(origin) for origin in parsed]
    except json.JSONDecodeError:
        pass

    # Fallback for comma-separated values.
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


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


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"message": "Shopping Cart API running"}


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
