from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.finance import (
    FinanceCreate,
    FinanceResponse,
    FinanceBalanceResponse,
)

from app.services.finance_service import FinanceService


router = APIRouter(
    prefix="/finance",
    tags=["Finance"],
)



@router.post(
    "/",
    response_model=FinanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_finance(
    data: FinanceCreate,
    db: Session = Depends(get_db),
):

    service = FinanceService(db)

    try:

        return service.create_transaction(

            member_id=data.member_id,

            transaction_type=data.transaction_type,

            amount=data.amount,

            description=data.description,

        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )




@router.get(
    "/",
    response_model=list[FinanceResponse],
)
def list_finance(
    db: Session = Depends(get_db),
):

    service = FinanceService(db)

    return service.list_transactions()




@router.get(
    "/balance",
    response_model=FinanceBalanceResponse,
)
def finance_balance(
    db: Session = Depends(get_db),
):

    service = FinanceService(db)


    income = service.get_income()

    expense = service.get_expense()


    return FinanceBalanceResponse(

        total_income=income,

        total_expense=expense,

        balance=income - expense,

    )