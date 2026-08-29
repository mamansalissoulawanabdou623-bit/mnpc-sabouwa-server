import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


settings = get_settings()


password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(
    password: str,
) -> str:
    return password_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    subject: uuid.UUID | str,
) -> str:
    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(
    subject: uuid.UUID | str,
) -> tuple[str, datetime]:
    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            days=settings.refresh_token_expire_days
        )
    )

    token = secrets.token_urlsafe(64)

    payload = {
        "sub": str(subject),
        "exp": expiration,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }

    signed_token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return signed_token, expiration


def decode_token(
    token: str,
) -> dict:
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

    except JWTError as exc:
        raise ValueError(
            "Jeton invalide ou expire."
        ) from exc


def create_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_verification_code(
    code: str,
) -> str:
    return hashlib.sha256(
        code.encode("utf-8")
    ).hexdigest()


def hash_refresh_token(
    token: str,
) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()
