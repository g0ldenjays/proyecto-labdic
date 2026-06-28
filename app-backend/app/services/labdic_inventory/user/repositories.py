# app/services/labdic_inventory/user/repositories.py

from advanced_alchemy.filters import CollectionFilter
from advanced_alchemy.repository import SQLAlchemySyncRepository
from litestar.dto import DTOData
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.inventory import User
from app.services.labdic_inventory.role.repositories import RoleRepository

password_hasher = PasswordHash.recommended()


class UserRepository(SQLAlchemySyncRepository[User]):
    """Repositorio para operaciones CRUD de usuarios.

    Extiende SQLAlchemySyncRepository con métodos personalizados
    para manejo de roles y autenticación.
    """

    model_type = User

    def get_my_user(self, username: str) -> User:
        """Obtiene un usuario por su username con todas sus relaciones cargadas."""
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .options(selectinload(User.loan_requests))
            .options(selectinload(User.status_logs))
            .where(User.username == username)
        )
        return self.session.execute(stmt).scalar_one()

    def add_with_existing_roles(
        self, roles_repo: RoleRepository,
        user: User,
        **kwargs
    ) -> User:
        """Crea un usuario hasheando su contraseña y asignando roles existentes por ID.

        Models: Users & Roles + Auth Controllers
        """

        # Hashing the password before saving the user.
        user.password = password_hasher.hash(user.password)

        # Add a user with existing roles, matching by id.
        user.roles = roles_repo.list(
            CollectionFilter(
                field_name="id",
                values=[role.id for role in user.roles]
            )
        )

        self.add(user, **kwargs)

        return user

    def update_with_existing_roles(
        self, roles_repo: RoleRepository, user_id: int, user_data: DTOData[User], **kwargs
    ) -> User:
        """Update a user using existing roles, matching by id."""

        user_data_dict = user_data.as_builtins()

        if "roles" in user_data_dict:
            user_data_dict["roles"] = roles_repo.list(
                CollectionFilter(
                    field_name="id",
                    values=[role.id for role in user_data_dict["roles"]]
                )
            )

        user, _ = self.get_and_update(
            id=user_id,
            **user_data_dict,
            match_fields=["id"],
            **kwargs
        )

        return user

    def check_password(self, username: str, password: str) -> bool:
        user = self.get(username, id_attribute="username")

        return password_hasher.verify(password, user.password)
    
    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalar_one_or_none()


    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def create_user(
        self,
        rut: str,
        name: str,
        username: str,
        email: str,
        password: str,
        is_admin: bool = False,
        is_active: bool = True,
    ) -> User:
        user = User(
            rut=rut,
            name=name,
            username=username,
            email=email,
            password=password,
            is_admin=is_admin,
            is_active=is_active,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

def provide_user_repository(db_session: Session) -> UserRepository:
    """
    Provide a SQLAlchemySyncRepository for User.
    """
    return UserRepository(session=db_session)
