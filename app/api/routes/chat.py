import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatGroupCreate,
    ChatGroupResponse,
    ChatMessageCreate,
    ChatMessageResponse,
)
from app.services.chat import chat_service


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/groups",
    response_model=ChatGroupResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chat_group(
    data: ChatGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = chat_service.create_group(
        db=db,
        name=data.name,
        description=data.description,
        group_type=data.group_type,
    )

    chat_service.add_member(
        db=db,
        group_id=group.id,
        user_id=current_user.id,
        role="ADMIN",
    )

    return ChatGroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        group_type=group.group_type,
        is_active=group.is_active,
        created_at=group.created_at,
        updated_at=group.updated_at,
        members_count=1,
    )


@router.get(
    "/groups",
    response_model=list[ChatGroupResponse],
)
def list_chat_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    groups = chat_service.get_groups(db)

    result = []

    for group, members_count in groups:
        result.append(
            ChatGroupResponse(
                id=group.id,
                name=group.name,
                description=group.description,
                group_type=group.group_type,
                is_active=group.is_active,
                created_at=group.created_at,
                updated_at=group.updated_at,
                members_count=members_count,
            )
        )

    return result


@router.get(
    "/groups/{group_id}/members",
)
def list_group_members(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = chat_service.get_group(
        db=db,
        group_id=group_id,
    )

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe introuvable.",
        )

    if not chat_service.is_group_member(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas membre de ce groupe.",
        )

    return chat_service.get_group_members(
        db=db,
        group_id=group_id,
    )


@router.post(
    "/groups/{group_id}/members/{user_id}",
)
def add_chat_member(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = chat_service.get_group(
        db=db,
        group_id=group_id,
    )

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe introuvable.",
        )

    if not chat_service.is_group_member(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas membre de ce groupe.",
        )

    member = chat_service.add_member(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    return member


@router.delete(
    "/groups/{group_id}/members/{user_id}",
)
def remove_chat_member(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not chat_service.is_group_member(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas membre de ce groupe.",
        )

    removed = chat_service.remove_member(
        db=db,
        group_id=group_id,
        user_id=user_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membre introuvable.",
        )

    return {
        "status": "ok",
        "message": "Membre retiré du groupe.",
    }


@router.get(
    "/groups/{group_id}/messages",
    response_model=list[ChatMessageResponse],
)
def list_messages(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = chat_service.get_group(
        db=db,
        group_id=group_id,
    )

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe introuvable.",
        )

    if not chat_service.is_group_member(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas membre de ce groupe.",
        )

    return chat_service.get_messages(
        db=db,
        group_id=group_id,
    )


@router.post(
    "/groups/{group_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    group_id: uuid.UUID,
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = chat_service.get_group(
        db=db,
        group_id=group_id,
    )

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Groupe introuvable.",
        )

    if not chat_service.is_group_member(
        db=db,
        group_id=group_id,
        user_id=current_user.id,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas membre de ce groupe.",
        )

    if (
        data.message is None
        and data.media_url is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le message ou le média est requis.",
        )

    return chat_service.create_message(
        db=db,
        group_id=group_id,
        sender_id=current_user.id,
        message_type=data.message_type,
        message=data.message,
        media_url=data.media_url,
        file_name=data.file_name,
    )
