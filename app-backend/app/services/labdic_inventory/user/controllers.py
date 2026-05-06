# app/services/labdic_inventory/user/controllers.py

from typing import Any, Sequence

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, Request, Response, delete, get, patch, post
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import Token
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.handlers import BaseRouteHandler

from app.models.inventory import User

# Esta es la forma de importar para colaborar con otro repositorio
from ..role.repositories import RoleRepository, provide_role_repository
from .dtos import UserCreateDTO, UserReadDTO, UserUpdateDTO
from .repositories import UserRepository, provide_user_repository

# GUARDS

def admin_user_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard que restringe el acceso a administradores."""
    if not connection.user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized.",
        )

def require_active(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard que restringe el acceso a usuarios inactivos."""
    if not connection.user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta de usuario inactiva.")

def not_found_error_handler(_: Request[Any, Any, Any], __: NotFoundError) -> Response[Any]:
    return Response(status_code=404, content={"status_code": 404, "detail": "User not found"})


class UserController(Controller):
    path = "/users"
    guards = [require_active]   # Requiere que el usuario este activo para ejecutar CRUDs.
    tags = ["users"]
    return_dto = UserReadDTO
    dependencies = {"users_repo": Provide(provide_user_repository, sync_to_thread=False)}
    exception_handlers = {NotFoundError: not_found_error_handler}

    @get("/me")
    async def get_my_user(self, request: "Request[User, Token, Any]") -> User:
        return request.user

    @get(path="/", summary="ListUsers")
    async def list(self, users_repo: UserRepository) -> Sequence[User]:
        """List all users."""
        return users_repo.list()

    @get(path="/{user_id:int}", summary="GetUser")
    async def fetch(self, user_id: int, users_repo: UserRepository) -> User:
        """Get a user by ID."""
        return users_repo.get_one(id=user_id)

    # Arreglar para que al crear usuario se le asignen roles.
    @post(
        path="/",
        summary="CreateUser",
        dto=UserCreateDTO,
        guards=[admin_user_guard],
        dependencies={"roles_repo": Provide(provide_role_repository, sync_to_thread=False)},
    )
    async def create(
        self,
        data: User,
        users_repo: UserRepository,
        roles_repo: RoleRepository,
    ) -> User:
        """Create a new user with role."""
        return users_repo.add_with_existing_roles(roles_repo, data, auto_commit=True)

    @patch(
        path="/{user_id:int}",
        summary="UpdateUser",
        dto=UserUpdateDTO,
        guards=[admin_user_guard],
        dependencies={"roles_repo": Provide(provide_role_repository, sync_to_thread=False)},
    )
    async def update(
        self,
        user_id: int,
        data: DTOData[User],
        users_repo: UserRepository,
        roles_repo: RoleRepository,
    ) -> User:
        """Update an existing user."""
        return users_repo.update_with_existing_roles(
            roles_repo,
            user_id,
            data,
            auto_commit=True,
        )

    @delete(
        path="/{user_id:int}",
        summary="DeleteUser",
        guards=[admin_user_guard],
    )
    async def delete(self, user_id: int, users_repo: UserRepository) -> None:
        """Delete a user by ID."""
        users_repo.delete(user_id, auto_commit=True)
