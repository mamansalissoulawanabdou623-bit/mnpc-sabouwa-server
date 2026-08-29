from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create_document(
        self,
        *,
        title: str,
        description: str | None,
        document_type: str,
        file_url: str,
        created_by: UUID | None,
    ) -> Document:

        document = Document(
            title=title,
            description=description,
            document_type=document_type.upper(),
            file_url=file_url,
            created_by=created_by,
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def list_documents(
        self,
    ) -> list[Document]:

        return list(
            self.db.scalars(
                select(Document)
                .order_by(
                    Document.created_at.desc()
                )
            ).all()
        )

    def get_document(
        self,
        document_id: UUID,
    ) -> Document | None:

        return self.db.get(
            Document,
            document_id,
        )

    def update_document(
        self,
        document_id: UUID,
        *,
        title: str | None = None,
        description: str | None = None,
        document_type: str | None = None,
        file_url: str | None = None,
    ) -> Document:

        document = self.db.get(
            Document,
            document_id,
        )

        if document is None:
            raise ValueError(
                "Document introuvable."
            )

        if title is not None:
            document.title = title

        if description is not None:
            document.description = description

        if document_type is not None:
            document.document_type = document_type.upper()

        if file_url is not None:
            document.file_url = file_url

        self.db.commit()
        self.db.refresh(document)

        return document

    def delete_document(
        self,
        document_id: UUID,
    ) -> None:

        document = self.db.get(
            Document,
            document_id,
        )

        if document is None:
            raise ValueError(
                "Document introuvable."
            )

        self.db.delete(document)
        self.db.commit()
