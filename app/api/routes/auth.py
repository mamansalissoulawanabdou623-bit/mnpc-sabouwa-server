import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db

from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegistrationResponse,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)

from app.services.auth_service import AuthService


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
)


# ============================================================
# AUTHENTIFICATION BEARER JWT
# ============================================================

security = HTTPBearer(
    scheme_name="BearerAuth",
    description=(
        "Entrez votre access token JWT. "
        "Swagger ajoutera automatiquement : "
        "Authorization: Bearer <token>"
    ),
)


# ============================================================
# INSCRIPTION
# ============================================================

@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
) -> RegistrationResponse:

    service = AuthService(db)

    try:
        return service.register(data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


# ============================================================
# VERIFICATION EMAIL
# ============================================================

@router.post(
    "/verify-email",
    response_model=AuthResponse,
)
def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:

    service = AuthService(db)

    try:
        return service.verify_email(
            email=data.email,
            code=data.code,
        )

    except ValueError as exc:
        print(
            "ERREUR VERIFICATION EMAIL :",
            str(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ============================================================
# RENVOI CODE VERIFICATION
# ============================================================

@router.post(
    "/resend-verification",
    response_model=MessageResponse,
)
def resend_verification(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:

    service = AuthService(db)

    try:
        service.resend_verification(
            email=data.email,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return MessageResponse(
        message=(
            "Si le compte existe et n'est pas encore "
            "verifie, un nouveau code a ete envoye."
        )
    )


# ============================================================
# CONNEXION
# ============================================================

@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:

    service = AuthService(db)

    try:
        return service.login(data)

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:

    service = AuthService(db)

    try:
        return service.refresh(
            data.refresh_token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


# ============================================================
# DECONNEXION
# ============================================================

@router.post(
    "/logout",
    response_model=MessageResponse,
)
def logout(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:

    service = AuthService(db)

    service.logout(
        data.refresh_token,
    )

    return MessageResponse(
        message="Deconnexion effectuee.",
    )


# ============================================================
# MOT DE PASSE OUBLIE
# ============================================================

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:

    return MessageResponse(
        message=(
            "Si cette adresse est associee a un compte, "
            "les instructions de recuperation seront envoyees."
        )
    )


# ============================================================
# UTILISATEUR CONNECTE
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
    db: Session = Depends(get_db),
) -> UserResponse:

    # --------------------------------------------------------
    # TOKEN
    # --------------------------------------------------------

    token = credentials.credentials

    # --------------------------------------------------------
    # DECODAGE JWT
    # --------------------------------------------------------

    try:
        payload = decode_token(token)

        # Seul un access token est accepté.
        if payload.get("type") != "access":
            raise ValueError(
                "Le token fourni n'est pas un access token."
            )

        user_id = uuid.UUID(
            str(payload.get("sub")),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'acces invalide.",
        ) from exc

    # --------------------------------------------------------
    # RECHERCHE UTILISATEUR
    # --------------------------------------------------------

    service = AuthService(db)

    try:
        user = service.get_user(
            user_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Adresse e-mail non verifiee.",
        )

    # --------------------------------------------------------
    # STATUT COMPTE
    # --------------------------------------------------------

    if user.account_status in {
        "SUSPENDED",
        "DISABLED",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte non autorise.",
        )

    # --------------------------------------------------------
    # REPONSE
    # --------------------------------------------------------

    return service.to_response(user)

