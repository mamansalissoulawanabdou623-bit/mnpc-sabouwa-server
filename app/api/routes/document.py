from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "/",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    return service.list_documents()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    service = DocumentService(db)

    document = service.get_document(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document introuvable.",
        )

    return document


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = DocumentService(db)

    return service.create_document(
        title=data.title,
        description=data.description,
        document_type=data.document_type,
        file_url=data.file_url,
        created_by=admin.id,
    )


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
)
def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = DocumentService(db)

    try:
        return service.update_document(
            document_id,
            title=data.title,
            description=data.description,
            document_type=data.document_type,
            file_url=data.file_url,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    service = DocumentService(db)

    try:
        service.delete_document(
            document_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
