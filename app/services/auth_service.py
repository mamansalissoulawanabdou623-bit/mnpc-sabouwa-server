import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_verification_code,
    decode_token,
    hash_password,
    hash_refresh_token,
    hash_verification_code,
    verify_password,
)
from app.models.email_verification import EmailVerificationCode
from app.models.member import Member
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegistrationResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.email_service import send_verification_email


settings = get_settings()


class AuthService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def register(
        self,
        data: RegisterRequest,
    ) -> RegistrationResponse:

        email = data.email.lower().strip()

        existing_user = self.db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing_user is not None:
            raise ValueError(
                "Cette adresse e-mail est deja utilisee."
            )

        user = User(
            email=email,
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            phone=data.phone.strip(),
            password_hash=hash_password(
                data.password
            ),
            role="MEMBRE",
            account_status="PENDING",
            email_verified=False,
        )

        self.db.add(user)

        try:
            self.db.flush()

            self._create_verification_code(
                user
            )

            self.db.commit()

            self.db.refresh(user)

        except Exception:
            self.db.rollback()
            raise

        return RegistrationResponse(
            user=self.to_response(user),
            email_verification_required=True,
        )

    def verify_email(
        self,
        email: str,
        code: str,
    ) -> AuthResponse:

        normalized_email = (
            email.lower().strip()
        )

        user = self.db.scalar(
            select(User).where(
                User.email == normalized_email
            )
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        if user.email_verified:
            raise ValueError(
                "Cette adresse e-mail est deja verifiee."
            )

        verification = self.db.scalar(
            select(EmailVerificationCode)
            .where(
                EmailVerificationCode.user_id
                == user.id,
                EmailVerificationCode.used_at.is_(
                    None
                ),
            )
            .order_by(
                EmailVerificationCode.created_at.desc()
            )
        )

        if verification is None:
            raise ValueError(
                "Aucun code de verification actif."
            )

        now = datetime.now(
            timezone.utc
        )

        expires_at = verification.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at < now:
            raise ValueError(
                "Le code de verification a expire."
            )

        if verification.attempts >= 5:
            raise ValueError(
                "Nombre maximal de tentatives atteint."
            )

        code_hash = hash_verification_code(
            code.strip()
        )

        if code_hash != verification.code_hash:

            verification.attempts += 1

            self.db.commit()

            raise ValueError(
                "Code de verification incorrect."
            )

        verification.used_at = now

        user.email_verified = True
        user.account_status = "ACTIVE"

        access_token = create_access_token(
            user.id
        )

        refresh_token, refresh_expiration = (
            create_refresh_token(
                user.id
            )
        )

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(
                refresh_token
            ),
            expires_at=refresh_expiration,
        )

        self.db.add(
            refresh_record
        )

        try:
            self.db.commit()

            self.db.refresh(user)

        except Exception:
            self.db.rollback()
            raise

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self.to_response(user),
        )

    def resend_verification(
        self,
        email: str,
    ) -> None:

        normalized_email = (
            email.lower().strip()
        )

        user = self.db.scalar(
            select(User).where(
                User.email == normalized_email
            )
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        if user.email_verified:
            raise ValueError(
                "Cette adresse e-mail est deja verifiee."
            )

        self._invalidate_active_codes(
            user.id
        )

        try:

            self._create_verification_code(
                user
            )

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

    def login(
        self,
        data: LoginRequest,
    ) -> AuthResponse:

        email = data.email.lower().strip()

        user = self.db.scalar(
            select(User).where(
                User.email == email
            )
        )

        if user is None:
            raise ValueError(
                "E-mail ou mot de passe incorrect."
            )

        if not verify_password(
            data.password,
            user.password_hash,
        ):
            raise ValueError(
                "E-mail ou mot de passe incorrect."
            )

        if not user.email_verified:
            raise ValueError(
                "Adresse e-mail non verifiee."
            )

        if user.account_status in {
            "SUSPENDED",
            "DISABLED",
        }:
            raise ValueError(
                "Compte non autorise."
            )

        now = datetime.now(
            timezone.utc
        )

        user.last_login_at = now

        access_token = create_access_token(
            user.id
        )

        refresh_token, refresh_expiration = (
            create_refresh_token(
                user.id
            )
        )

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(
                refresh_token
            ),
            expires_at=refresh_expiration,
        )

        self.db.add(
            refresh_record
        )

        try:

            self.db.commit()

            self.db.refresh(user)

        except Exception:
            self.db.rollback()
            raise

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self.to_response(user),
        )

    def refresh(
        self,
        refresh_token: str,
    ) -> TokenResponse:

        token_hash = hash_refresh_token(
            refresh_token
        )

        stored_token = self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash
                == token_hash,
                RefreshToken.revoked_at.is_(
                    None
                ),
            )
        )

        if stored_token is None:
            raise ValueError(
                "Refresh token invalide."
            )

        now = datetime.now(
            timezone.utc
        )

        expires_at = stored_token.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if expires_at < now:
            raise ValueError(
                "Refresh token expire."
            )

        user = self.db.get(
            User,
            stored_token.user_id,
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        if not user.email_verified:
            raise ValueError(
                "Adresse e-mail non verifiee."
            )

        if user.account_status in {
            "SUSPENDED",
            "DISABLED",
        }:
            raise ValueError(
                "Compte non autorise."
            )

        new_access_token = create_access_token(
            user.id
        )

        new_refresh_token, new_refresh_expiration = (
            create_refresh_token(
                user.id
            )
        )

        stored_token.revoked_at = now

        new_refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(
                new_refresh_token
            ),
            expires_at=new_refresh_expiration,
        )

        self.db.add(
            new_refresh_record
        )

        try:

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    def logout(
        self,
        refresh_token: str,
    ) -> None:

        self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash
                == hash_refresh_token(
                    refresh_token
                ),
                RefreshToken.revoked_at.is_(
                    None
                ),
            )
            .values(
                revoked_at=datetime.now(
                    timezone.utc
                )
            )
        )

        self.db.commit()

    def get_user(
        self,
        user_id: uuid.UUID,
    ) -> User:

        user = self.db.get(
            User,
            user_id,
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        return user

    def to_response(
        self,
        user: User,
    ) -> UserResponse:

        member = self.db.scalar(
            select(Member).where(
                Member.user_id == user.id
            )
        )

        member_id = (
            member.id
            if member is not None
            else None
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            role=user.role,
            account_status=user.account_status,
            email_verified=user.email_verified,
            member_id=member_id,
            last_login_at=user.last_login_at,
        )

    def _create_verification_code(
        self,
        user: User,
    ) -> None:

        code = create_verification_code()

        code_hash = hash_verification_code(
            code
        )

        expiration = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=settings.verification_code_minutes
            )
        )

        verification = EmailVerificationCode(
            user_id=user.id,
            code_hash=code_hash,
            expires_at=expiration,
            attempts=0,
        )

        self.db.add(
            verification
        )

        send_verification_email(
            recipient=user.email,
            code=code,
        )

    def _invalidate_active_codes(
        self,
        user_id: uuid.UUID,
    ) -> None:

        self.db.execute(
            update(
                EmailVerificationCode
            )
            .where(
                EmailVerificationCode.user_id
                == user_id,
                EmailVerificationCode.used_at.is_(
                    None
                ),
            )
            .values(
                used_at=datetime.now(
                    timezone.utc
                )
            )
        )