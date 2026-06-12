from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.inventory import Book

class BookRepository(SQLAlchemySyncRepository[Book]):
    model_type = Book

    def list_active(self) -> list[Book]:
        stmt = (
            select(Book)
            .where(Book.is_active.is_(True))
            .order_by(Book.title.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def create_book(
        self,
        title: str,
        author: str | None = None,
        isbn: str | None = None,
        topic: str | None = None,
        description: str | None = None,
        total_quantity: int = 1,
        available_quantity: int | None = None,
        is_active: bool = True,
    ) -> Book:
        if available_quantity is None:
            available_quantity = total_quantity

        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            topic=topic,
            description=description,
            total_quantity=total_quantity,
            available_quantity=available_quantity,
            is_active=is_active,
        )

        self.session.add(book)
        self.session.commit()
        self.session.refresh(book)
        return book

    def update_book(self, book_id: int, data: dict) -> Book:
        book = self.session.get(Book, book_id)

        for field, value in data.items():
            if value is not None:
                setattr(book, field, value)

        self.session.commit()
        self.session.refresh(book)
        return book

def provide_book_repository(db_session: Session) -> BookRepository:
    return BookRepository(session=db_session)