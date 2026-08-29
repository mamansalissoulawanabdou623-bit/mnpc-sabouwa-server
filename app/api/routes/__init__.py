from app.api.routes.finance import router as finance_router
from app.api.routes.member import router as member_router
from app.api.routes.organization import router as organization_router
from app.api.routes.organization_responsible import (
    router as organization_responsible_router,
)
from app.api.routes.statistic import router as statistic_router


__all__ = [
    "member_router",
    "organization_router",
    "organization_responsible_router",
    "statistic_router",
    "finance_router",
]