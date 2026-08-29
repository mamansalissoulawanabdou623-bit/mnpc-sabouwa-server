import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chat.chat_group import ChatGroup
from app.models.chat.chat_group_member import ChatGroupMember
from app.models.chat.chat_message import ChatMessage


def create_group(
    db: Session,
    name: str,
    description: str | None = None,
    group_type: str = "GENERAL",
) -> ChatGroup:
    group = ChatGroup(
        name=name,
        description=description,
        group_type=group_type,
        is_active=True,
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return group


def get_groups(
    db: Session,
) -> list[tuple[ChatGroup, int]]:
    statement = (
        select(
            ChatGroup,
            func.count(ChatGroupMember.id).label("members_count"),
        )
        .outerjoin(
            ChatGroupMember,
            ChatGroupMember.group_id == ChatGroup.id,
        )
        .where(
            ChatGroup.is_active.is_(True),
        )
        .group_by(
            ChatGroup.id,
        )
        .order_by(
            ChatGroup.created_at.desc(),
        )
    )

    return list(
        db.execute(statement).all()
    )


def get_group(
    db: Session,
    group_id: uuid.UUID,
) -> ChatGroup | None:
    return db.scalar(
        select(ChatGroup).where(
            ChatGroup.id == group_id,
        )
    )


def add_member(
    db: Session,
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str = "MEMBER",
) -> ChatGroupMember:
    existing = db.scalar(
        select(ChatGroupMember).where(
            ChatGroupMember.group_id == group_id,
            ChatGroupMember.user_id == user_id,
        )
    )

    if existing is not None:
        return existing

    member = ChatGroupMember(
        group_id=group_id,
        user_id=user_id,
        role=role,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def remove_member(
    db: Session,
    group_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    member = db.scalar(
        select(ChatGroupMember).where(
            ChatGroupMember.group_id == group_id,
            ChatGroupMember.user_id == user_id,
        )
    )

    if member is None:
        return False

    db.delete(member)
    db.commit()

    return True


def get_group_members(
    db: Session,
    group_id: uuid.UUID,
) -> list[ChatGroupMember]:
    statement = (
        select(ChatGroupMember)
        .where(
            ChatGroupMember.group_id == group_id,
        )
        .order_by(
            ChatGroupMember.joined_at.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )


def is_group_member(
    db: Session,
    group_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    member = db.scalar(
        select(ChatGroupMember.id).where(
            ChatGroupMember.group_id == group_id,
            ChatGroupMember.user_id == user_id,
        )
    )

    return member is not None


def create_message(
    db: Session,
    group_id: uuid.UUID,
    sender_id: uuid.UUID,
    message_type: str = "TEXT",
    message: str | None = None,
    media_url: str | None = None,
    file_name: str | None = None,
) -> ChatMessage:
    chat_message = ChatMessage(
        group_id=group_id,
        sender_id=sender_id,
        message_type=message_type,
        message=message,
        media_url=media_url,
        file_name=file_name,
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)

    return chat_message


def get_messages(
    db: Session,
    group_id: uuid.UUID,
) -> list[ChatMessage]:
    statement = (
        select(ChatMessage)
        .where(
            ChatMessage.group_id == group_id,
        )
        .order_by(
            ChatMessage.created_at.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )
