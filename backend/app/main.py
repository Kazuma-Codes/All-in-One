from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .api.v1.router import api_router
from .core.rate_limit import limiter
from .core.observability import init_sentry
from .core.config import settings
from .core.database import SessionLocal
from .core.bootstrap import ensure_admin_user

logger = logging.getLogger("universal-converter")

if settings.APP_ENV == "production" and settings.SECRET_KEY == "super-secret-key-change-in-prod":
    raise RuntimeError(
        "SECRET_KEY is the insecure default. Set a strong SECRET_KEY before running in production."
    )

init_sentry()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db = SessionLocal()
    try:
        message = ensure_admin_user(db)
        if message:
            logger.warning(message)
    finally:
        db.close()
    yield


app = FastAPI(title="Universal Converter API", lifespan=lifespan)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )


# CORS Configuration
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"service": "universal-converter"}