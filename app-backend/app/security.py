from typing import Any

from litestar.connection import ASGIConnection
from litestar.contrib.jwt import OAuth2PasswordBearerAuth, Token
from litestar.exceptions import NotFoundException
from litestar.repository import NotFoundError

from app.config import settings  # Listo.
from app.database import sqlalchemy_config  # Listo.
from app.models.inventory import User  # Listo.
from app.services.labdic_inventory.user.repositories import UserRepository  # Listo.


async def retrieve_user_handler(
    token: Token,
    _: ASGIConnection[Any, Any, Any, Any],
) -> User:
    session_maker = sqlalchemy_config.create_session_maker()
    try:
        with session_maker() as session:
            users_repo = UserRepository(session=session)
            return users_repo.get_my_user(username=token.sub)
    except NotFoundError as e:
        raise NotFoundException("Usuario no encontrado") from e

oauth2_auth = OAuth2PasswordBearerAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=settings.secret_key.get_secret_value(),
    token_url="/labdic_inventory/auth/login",
    exclude=["/labdic_inventory/auth/login", "/labdic_inventory/auth/google-register", "/schema"],
)
