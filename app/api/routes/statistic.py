from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.statistic import (
    NationalStatisticCreate,
    NationalStatisticResponse,
)
from app.services.statistic_service import StatisticService


router = APIRouter(
    prefix="/statistics",
    tags=["Statistiques"],
)


@router.post(
    "/",
    response_model=NationalStatisticResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_statistic(
    data: NationalStatisticCreate,
    db: Session = Depends(get_db),
):
    service = StatisticService(db)

    return service.create_statistic(
        statistic_type=data.statistic_type,
        year=data.year,
        region=data.region,
        department=data.department,
        commune=data.commune,
        total_members=data.total_members,
        total_men=data.total_men,
        total_women=data.total_women,
        total_youth=data.total_youth,
    )


@router.get(
    "/",
    response_model=list[NationalStatisticResponse],
)
def list_statistics(
    db: Session = Depends(get_db),
):
    service = StatisticService(db)

    return service.list_statistics()
