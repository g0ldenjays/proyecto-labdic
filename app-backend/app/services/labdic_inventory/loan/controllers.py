# app/services/labdic_inventory/loan/controllers.py

from typing import Any, Sequence

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, Request, Response, delete, get, patch, post
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import Token
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.handlers import BaseRouteHandler

from app.models.inventory import LoanRequest, User

from .dtos import LoanRequestCreateDTO, LoanRequestReadDTO
from .repositories import LoanRequestRepository, provide_loan_repository


def admin_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    if not connection.user.is_admin:
        raise HTTPException(status_code=403, detail="No autorizado.")


def not_found_error_handler(_: Request[Any, Any, Any], __: NotFoundError) -> Response[Any]:
    return Response(status_code=404, content={"status_code": 404, "detail": "Solicitud no encontrada"})


class LoanRequestController(Controller):
    path = "/loans"
    tags = ["loans"]
    return_dto = LoanRequestReadDTO
    dependencies = {"loans_repo": Provide(provide_loan_repository, sync_to_thread=False)}
    exception_handlers = {NotFoundError: not_found_error_handler}

    @get(path="/", summary="ListLoanRequests", guards=[admin_guard])
    async def list(self, loans_repo: LoanRequestRepository) -> Sequence[LoanRequest]:
        """Lista todas las solicitudes con relaciones. Solo administradores."""
        return loans_repo.list_with_relations()

    @get(path="/me", summary="ListMyLoanRequests")
    async def list_mine(
        self,
        request: Request[User, Token, Any],
        loans_repo: LoanRequestRepository,
    ) -> Sequence[LoanRequest]:
        """Lista las solicitudes del usuario autenticado con relaciones."""
        return loans_repo.list_mine(user_id=request.user.id)

    @get(path="/{loan_id:int}", summary="GetLoanRequest")
    async def fetch(self, loan_id: int, loans_repo: LoanRequestRepository) -> LoanRequest:
        """Detalle de una solicitud con sus items y devices."""
        return loans_repo.get_with_relations(loan_id)

    @post(path="/", summary="CreateLoanRequest")
    async def create(
        self,
        data: LoanRequestCreateDTO,
        request: Request[User, Token, Any],
        loans_repo: LoanRequestRepository,
    ) -> LoanRequest:
        """Crea una solicitud de préstamo.
        Si el usuario autenticado es administrador, puede crear la solicitud en nombre de otro usuario.
        """
        requested_user_id = data.requested_user_id

        if requested_user_id is not None and not request.user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Solo un administrador puede solicitar en nombre de otro usuario.",
            )

        target_user_id = requested_user_id or request.user.id

        if not loans_repo.user_exists(target_user_id):
            raise HTTPException(
                status_code=400,
                detail="El usuario solicitante no existe.",
            )

        return loans_repo.create_with_items(
            user_id=target_user_id,
            device_ids=data.device_ids,
            reason=data.reason,
            estimated_return_date=data.estimated_return_date,
        )

    @patch(path="/{loan_id:int}/approve", summary="ApproveLoanRequest", guards=[admin_guard])
    async def approve(self, loan_id: int, loans_repo: LoanRequestRepository) -> LoanRequest:
        return loans_repo.approve(loan_id)

    @patch(path="/{loan_id:int}/reject", summary="RejectLoanRequest", guards=[admin_guard])
    async def reject(self, loan_id: int, loans_repo: LoanRequestRepository) -> LoanRequest:
        return loans_repo.reject(loan_id)

    @patch(path="/{loan_id:int}/deliver", summary="DeliverLoanRequest", guards=[admin_guard])
    async def deliver(self, loan_id: int, loans_repo: LoanRequestRepository) -> LoanRequest:
        return loans_repo.deliver(loan_id)

    @patch(path="/{loan_id:int}/return", summary="ReturnLoanRequest", guards=[admin_guard])
    async def register_return(self, loan_id: int, loans_repo: LoanRequestRepository) -> LoanRequest:
        return loans_repo.register_return(loan_id)

    @delete(path="/{loan_id:int}", summary="DeleteLoanRequest", guards=[admin_guard])
    async def delete(self, loan_id: int, loans_repo: LoanRequestRepository) -> None:
        loans_repo.delete(loan_id, auto_commit=True)