from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.swagger import custom_openapi

from app.db.session import Base, engine

from app.api.routes.auth import router as auth_router
from app.api.routes.member import router as member_router
from app.api.routes.organization import router as organization_router
from app.api.routes.organization_responsible import (
    router as organization_responsible_router,
)
from app.api.routes.statistic import router as statistic_router
from app.api.routes.finance import router as finance_router
from app.api.routes.membership import router as membership_router
from app.api.routes.admin import router as admin_router
from app.api.routes.membership_payment import (
    router as membership_payment_router,
)
from app.api.routes.document import router as document_router
from app.api.routes.chat import router as chat_router

from app import models  # noqa: F401


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.app_env == "development":
        Base.metadata.create_all(
            bind=engine
        )

    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)


app.openapi = lambda: custom_openapi(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Routes API
# =========================

app.include_router(
    auth_router
)

app.include_router(
    member_router
)

app.include_router(
    organization_router
)

app.include_router(
    organization_responsible_router
)

app.include_router(
    statistic_router
)

app.include_router(
    admin_router
)

app.include_router(
    finance_router
)

app.include_router(
    membership_router
)

app.include_router(
    membership_payment_router
)

app.include_router(
    document_router
)

app.include_router(
    chat_router
)


@app.get("/")
def home():
    return {
        "application": "MNPC SABOUWA",
        "status": "API opérationnelle",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
