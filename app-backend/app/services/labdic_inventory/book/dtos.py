from dataclasses import dataclass
from advanced_alchemy.extensions.litestar import SQLAlchemyDTOConfig
from litestar.plugins.sqlalchemy import SQLAlchemyDTO
from app.models.inventory import Book

class BookReadDTO(SQLAlchemyDTO[Book]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "loan_request_items",
        },
        partial=True,
    )

@dataclass
class BookCreateDTO:
    title: str
    author: str | None = None
    isbn: str | None = None
    topic: str | None = None
    description: str | None = None
    total_quantity: int = 1
    available_quantity: int | None = None
    is_active: bool = True

@dataclass
class BookUpdateDTO:
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    topic: str | None = None
    description: str | None = None
    total_quantity: int | None = None
    available_quantity: int | None = None
    is_active: bool | None = None