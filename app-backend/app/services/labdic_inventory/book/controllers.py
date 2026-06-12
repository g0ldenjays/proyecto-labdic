from litestar import Controller, get, post, patch
from litestar.di import Provide
from app.models.inventory import Book
from app.services.labdic_inventory.book.dtos import (
    BookCreateDTO,
    BookReadDTO,
    BookUpdateDTO,
)
from app.services.labdic_inventory.book.repositories import (
    BookRepository,
    provide_book_repository,
)

class BookController(Controller):
    path = "/books"
    dependencies = {"books_repo": Provide(provide_book_repository, sync_to_thread=False)}

    @get("/", return_dto=BookReadDTO, sync_to_thread=False)
    def list_books(self, books_repo: BookRepository) -> list[Book]:
        return books_repo.list_active()

    @post("/", dto=None, return_dto=BookReadDTO, sync_to_thread=False)
    def create_book(
        self,
        data: BookCreateDTO,
        books_repo: BookRepository,
    ) -> Book:
        return books_repo.create_book(
            title=data.title,
            author=data.author,
            isbn=data.isbn,
            topic=data.topic,
            description=data.description,
            total_quantity=data.total_quantity,
            available_quantity=data.available_quantity,
            is_active=data.is_active,
        )

    @patch("/{book_id:int}", dto=None, return_dto=BookReadDTO, sync_to_thread=False)
    def update_book(
        self,
        book_id: int,
        data: BookUpdateDTO,
        books_repo: BookRepository,
    ) -> Book:
        return books_repo.update_book(
            book_id=book_id,
            data={
                "title": data.title,
                "author": data.author,
                "isbn": data.isbn,
                "topic": data.topic,
                "description": data.description,
                "total_quantity": data.total_quantity,
                "available_quantity": data.available_quantity,
                "is_active": data.is_active,
            },
        )
