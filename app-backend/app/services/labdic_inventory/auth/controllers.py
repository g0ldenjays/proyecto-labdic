from typing import Annotated

from litestar import Controller, Response, post
from litestar.contrib.jwt import OAuth2Login
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import settings
from app.models.inventory import User
from app.security import oauth2_auth
from app.services.labdic_inventory.auth.dtos import GoogleRegisterDTO
from app.services.labdic_inventory.user.repositories import (
    UserRepository,
    provide_user_repository,
)
from pwdlib import PasswordHash

from ..user.dtos import UserLoginDTO


password_hasher = PasswordHash.recommended()

class AuthController(Controller):
    path = "/auth"
    tags = ["auth"]

    @post(
        "/login",
        dto=UserLoginDTO,
        dependencies={"users_repo": Provide(provide_user_repository, sync_to_thread=False)},
    )
    async def login(
        self,
        data: Annotated[User, Body(media_type=RequestEncodingType.URL_ENCODED)],
        users_repo: UserRepository,
    ) -> Response[OAuth2Login]:
        user = users_repo.get_one_or_none(username=data.username)

        if user is None or not users_repo.check_password(data.username, data.password):
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrecta")

        return oauth2_auth.login(identifier=user.username)
    
    @post("/google-register", dto=None, sync_to_thread=True, dependencies={"users_repo": Provide(provide_user_repository, sync_to_thread=False)})
    def google_register(
        self,
        data: GoogleRegisterDTO,
        users_repo: UserRepository,
    ) -> dict:
        if data.password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")

        if len(data.password) < 6:
            raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres.")

        try:
            token_info = id_token.verify_oauth2_token(
                data.credential,
                google_requests.Request(),
                settings.google_client_id,
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="No se pudo verificar la cuenta de Google.")

        email = token_info.get("email")
        email_verified = token_info.get("email_verified")
        hosted_domain = token_info.get("hd")

        if not email or not email_verified:
            raise HTTPException(status_code=400, detail="El correo de Google no está verificado.")

        if not email.endswith(f"@{settings.allowed_google_domain}"):
            raise HTTPException(status_code=400, detail="Solo se permiten correos institucionales @umag.cl.")

        if hosted_domain and hosted_domain != settings.allowed_google_domain:
            raise HTTPException(status_code=400, detail="El dominio de Google no corresponde a UMAG.")

        username = email.split("@")[0]
        name = token_info.get("name") or username

        existing_email = users_repo.get_by_email(email)
        if existing_email:
            raise HTTPException(status_code=409, detail="Ya existe un usuario con este correo.")

        existing_username = users_repo.get_by_username(username)
        if existing_username:
            raise HTTPException(status_code=409, detail="Ya existe un usuario con este nombre de usuario.")

        user = users_repo.create_user(
            rut=data.rut or "",
            name=name,
            username=username,
            email=email,
            password=password_hasher.hash(data.password),
            is_admin=False,
            is_active=True,
        )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "message": "Usuario creado correctamente.",
        }

