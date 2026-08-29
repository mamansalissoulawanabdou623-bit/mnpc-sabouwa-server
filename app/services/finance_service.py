import uuid

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.finance import Finance


class FinanceService:


    def __init__(
        self,
        db: Session,
    ):
        self.db = db



    def create_transaction(
        self,
        *,
        transaction_type: str,
        amount: float,
        member_id: uuid.UUID | None = None,
        description: str | None = None,
    ) -> Finance:


        if amount <= 0:
            raise ValueError(
                "Le montant doit être supérieur à zéro."
            )


        allowed_types = [
            "COTISATION",
            "DON",
            "PARTENAIRE",
            "SUBVENTION",
            "DEPENSE",
        ]


        transaction_type = (
            transaction_type
            .upper()
            .strip()
        )


        if transaction_type not in allowed_types:
            raise ValueError(
                "Type de transaction invalide."
            )


        transaction = Finance(

            member_id=member_id,

            transaction_type=transaction_type,

            amount=amount,

            description=description,

            status="VALIDATED",

        )


        self.db.add(transaction)

        self.db.commit()

        self.db.refresh(transaction)


        return transaction




    def list_transactions(
        self,
    ) -> list[Finance]:

        return list(

            self.db.scalars(

                select(Finance)
                .order_by(
                    Finance.created_at.desc()
                )

            ).all()

        )




    def get_balance(
        self,
    ) -> float:


        total = self.db.scalar(

            select(
                func.sum(Finance.amount)
            )

        )


        return float(total or 0)





    def get_income(
        self,
    ) -> float:


        total = self.db.scalar(

            select(
                func.sum(Finance.amount)
            )
            .where(
                Finance.transaction_type != "DEPENSE"
            )

        )


        return float(total or 0)





    def get_expense(
        self,
    ) -> float:


        total = self.db.scalar(

            select(
                func.sum(Finance.amount)
            )
            .where(
                Finance.transaction_type == "DEPENSE"
            )

        )


        return float(total or 0)