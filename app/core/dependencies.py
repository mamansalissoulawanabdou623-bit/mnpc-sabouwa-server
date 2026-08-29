import uuid

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


def get_current_user(
    authorization: str | None = Header(
        default=None,
    ),
    db: Session = Depends(get_db),
) -> User:

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise.",
        )

    if not authorization.lower().startswith(
        "bearer "
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Format du token invalide.",
        )

    token = authorization[7:].strip()

    try:

        payload = decode_token(token)

        if payload.get("type") != "access":
            raise ValueError()

        user_id = uuid.UUID(
            str(payload.get("sub"))
        )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide.",
        )

    user = db.get(
        User,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable.",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email non vérifié.",
        )

    return user



def require_admin(
    user: User = Depends(get_current_user),
) -> User:

    if user.role != "ADMIN":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur requis.",
        )

    return user