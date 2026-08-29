from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class AdminDashboardResponse(BaseModel):

    total_users: int

    total_members: int

    pending_membership_requests: int

    total_finance_amount: float



class AdminUserResponse(BaseModel):

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

    created_at: datetime



class UpdateRoleRequest(BaseModel):

    role: str



class AdminMemberResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    user_id: UUID

    member_number: str

    membership_status: str