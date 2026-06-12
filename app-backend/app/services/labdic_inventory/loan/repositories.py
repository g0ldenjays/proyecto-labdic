# app/services/labdic_inventory/loan/repositories.py

from datetime import datetime, timezone

from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.inventory import Device, LoanRequest, LoanRequestItem, LoanRequestBookItem, Status, User


class LoanRequestRepository(SQLAlchemySyncRepository[LoanRequest]):
    model_type = LoanRequest

    def _get_status_id(self, name: str) -> int:
        """Obtiene el ID de un status por nombre."""
        stmt = select(Status).where(Status.name == name)
        status = self.session.execute(stmt).scalar_one()
        return status.id

    def _base_stmt(self):
        """Statement base con relaciones cargadas para todos los métodos de lista."""
        return (
            select(LoanRequest)
            .options(
                selectinload(LoanRequest.user),
                selectinload(LoanRequest.status),
                selectinload(LoanRequest.loan_request_items)
                    .selectinload(LoanRequestItem.device)
                    .selectinload(Device.product),
            )
        )

    def list_with_relations(self) -> list[LoanRequest]:
        """Lista todas las solicitudes con relaciones cargadas."""
        stmt = self._base_stmt().order_by(LoanRequest.id.desc())
        return list(self.session.execute(stmt).scalars().all())

    def list_mine(self, user_id: int) -> list[LoanRequest]:
        """Lista las solicitudes del usuario autenticado."""
        stmt = self._base_stmt().where(LoanRequest.user_id == user_id).order_by(LoanRequest.id.desc())
        return list(self.session.execute(stmt).scalars().all())

    def get_with_relations(self, loan_id: int) -> LoanRequest:
        """Obtiene una solicitud con todas sus relaciones cargadas."""
        stmt = self._base_stmt().where(LoanRequest.id == loan_id)
        return self.session.execute(stmt).scalar_one()

    def create_with_items(
        self,
        user_id: int,
        device_ids: list[int],
        reason: str | None,
        estimated_return_date: datetime | None,
        additional_items: str | None = None,
        book_ids: list[int] | None = None,
    ) -> LoanRequest:
        """Crea una solicitud de préstamo con sus items en una sola transacción."""
        status_id = self._get_status_id("pendiente")

        loan = LoanRequest(
            user_id=user_id,
            status_id=status_id,
            reason=reason,
            estimated_return_date=estimated_return_date,
            request_date=datetime.now(timezone.utc),
            additional_items=additional_items,
        )
        self.session.add(loan)
        self.session.flush()

        for device_id in device_ids:
            item = LoanRequestItem(
                loan_request_id=loan.id,
                device_id=device_id,
            )
            self.session.add(item)

        for book_id in book_ids or []:
            self.session.add(
                LoanRequestBookItem(
                    loan_request_id=loan.id,
                    book_id=book_id,
                    quantity=1,
                )
            )

        self.session.commit()
        return self.get_with_relations(loan.id)

    def approve(self, loan_id: int) -> LoanRequest:
        """Aprueba una solicitud y la deja inmediatamente en curso."""
        prestado_id = self._get_status_id("prestado")

        self.get_and_update(
            id=loan_id,
            status_id=prestado_id,
            delivery_date=datetime.now(timezone.utc),
            match_fields=["id"],
        )

        items = self.session.execute(
            select(LoanRequestItem).where(LoanRequestItem.loan_request_id == loan_id)
        ).scalars().all()

        for item in items:
            device = self.session.get(Device, item.device_id)
            if device:
                device.status_id = prestado_id

        self.session.commit()
        return self.get_with_relations(loan_id)

    def reject(self, loan_id: int) -> LoanRequest:
        """Rechaza una solicitud de préstamo."""
        status_id = self._get_status_id("rechazado")
        self.get_and_update(id=loan_id, status_id=status_id, match_fields=["id"], auto_commit=True)
        return self.get_with_relations(loan_id)

    def deliver(self, loan_id: int) -> LoanRequest:
        """Registra la entrega de los dispositivos al usuario."""
        prestado_id = self._get_status_id("prestado")

        self.get_and_update(
            id=loan_id,
            status_id=prestado_id,
            delivery_date=datetime.now(timezone.utc),
            match_fields=["id"],
        )

        items = self.session.execute(
            select(LoanRequestItem).where(LoanRequestItem.loan_request_id == loan_id)
        ).scalars().all()

        for item in items:
            device = self.session.get(Device, item.device_id)
            if device:
                device.status_id = prestado_id

        self.session.commit()
        return self.get_with_relations(loan_id)

    def register_return(self, loan_id: int) -> LoanRequest:
        """Registra la devolución de los dispositivos."""
        disponible_id = self._get_status_id("disponible")
        devuelto_id   = self._get_status_id("devuelto")  # ← fix: actualizar status de la solicitud

        self.get_and_update(
            id=loan_id,
            status_id=devuelto_id,              # ← fix: estaba faltando esto
            actual_return_date=datetime.now(timezone.utc),
            match_fields=["id"],
        )

        items = self.session.execute(
            select(LoanRequestItem).where(LoanRequestItem.loan_request_id == loan_id)
        ).scalars().all()

        for item in items:
            device = self.session.get(Device, item.device_id)
            if device:
                device.status_id = disponible_id

        self.session.commit()
        return self.get_with_relations(loan_id)
    
    def user_exists(self, user_id: int) -> bool:
        return self.session.get(User, user_id) is not None


def provide_loan_repository(db_session: Session) -> LoanRequestRepository:
    return LoanRequestRepository(session=db_session)