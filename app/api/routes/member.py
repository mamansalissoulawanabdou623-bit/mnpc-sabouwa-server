import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.core.dependencies import require_admin

from app.models.user import User

from app.schemas.member import (
    MemberCreate,
    MemberResponse,
)

from app.services.member_service import MemberService


router = APIRouter(
    prefix="/members",
    tags=["Membres"],
)


# Création manuelle d'un membre
# ADMIN uniquement
@router.post(
    "/",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_member(
    data: MemberCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = MemberService(db)

    try:

        return service.create_member(
            user_id=data.user_id,
            organization_unit_id=data.organization_unit_id,
            member_number=data.member_number,
            birth_date=data.birth_date,
            gender=data.gender,
            profession=data.profession,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error



# Liste des membres
# ADMIN uniquement
@router.get(
    "/",
    response_model=list[MemberResponse],
)
def list_members(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):

    service = MemberService(db)

    return service.list_members()



# Recherche par utilisateur
@router.get(
    "/user/{user_id}",
    response_model=MemberResponse,
)
def get_member_by_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
):

    service = MemberService(db)

    try:

        return service.get_member_by_user(
            user_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error



# Recherche par ID membre
@router.get(
    "/{member_id}",
    response_model=MemberResponse,
)
def get_member(
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
):

    service = MemberService(db)

    try:

        return service.get_member(
            member_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error