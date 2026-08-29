from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):

    first_name: str = Field(
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    phone: str = Field(
        min_length=6,
        max_length=30,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class VerifyEmailRequest(BaseModel):

    email: EmailStr

    code: str = Field(
        min_length=6,
        max_length=6,
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str


class ForgotPasswordRequest(BaseModel):

    email: EmailStr


class RefreshTokenRequest(BaseModel):

    refresh_token: str


class UserResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    email: EmailStr

    first_name: str

    last_name: str

    phone: str

    role: str

    account_status: str

    email_verified: bool

    member_id: UUID | None

    last_login_at: datetime | None


class RegistrationResponse(BaseModel):

    user: UserResponse

    email_verification_required: bool


class AuthResponse(BaseModel):

    access_token: str

    refresh_token: str

    user: UserResponse


class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str


class MessageResponse(BaseModel):

    message: str