# app/services/labdic_inventory/user/dtos.py

from advanced_alchemy.extensions.litestar import SQLAlchemyDTOConfig
from litestar.plugins.sqlalchemy import SQLAlchemyDTO

from app.models.inventory import User


class UserReadDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(
        exclude={"dispositivos", "administrative_documents"},
        partial=True,
    )

class UserCreateDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "loan_requests", "status_logs", "administrative_documents"},
        partial=False
    )

class UserUpdateDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "loan_requests", "status_logs", "password", "administrative_documents"},
        partial=True
    )

class UserLoginDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(include={"username", "password"})