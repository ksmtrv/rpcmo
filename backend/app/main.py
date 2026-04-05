from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import backups, categories, forecast, imports, mapping_templates, recurring, receivables, reports, rules, transactions
from app.core.db import init_db
from app.core.errors import AppError
from app.core.config import settings
from app.core.logging import setup_logging


def _cors_params() -> tuple[list[str], bool]:
    raw = (settings.cors_origins or "").strip()
    if raw == "*":
        return ["*"], False
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return ["*"], False
    cred = settings.cors_allow_credentials
    if "*" in parts:
        return ["*"], False
    return parts, cred


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    yield
    pass


app = FastAPI(
    title="Fincontrol",
    description="Local-first financial control for self-employed and microbusiness",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )

_origins, _cred = _cors_params()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_cred,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(imports.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(rules.router, prefix="/api/v1")
app.include_router(forecast.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(recurring.router, prefix="/api/v1")
app.include_router(mapping_templates.router, prefix="/api/v1")
app.include_router(receivables.router, prefix="/api/v1")
app.include_router(backups.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
