from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from app.models.inventory import Category, Device, Product, Status, Ubication, AdministrativeDocument, AdministrativeDocumentItem, DeviceStatusLog, LoanRequest, LoanRequestItem
from typing import Sequence
from datetime import datetime, timezone


class InventoryAdminRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count_total_devices(self) -> int:
        stmt = select(func.count(Device.id))
        return self.session.execute(stmt).scalar_one()

    def count_devices_by_status(self) -> list[tuple[str, int]]:
        stmt = (
            select(Status.name, func.count(Device.id))
            .join(Device, Device.status_id == Status.id)
            .group_by(Status.name)
            .order_by(Status.name)
        )
        return [(name, count) for name, count in self.session.execute(stmt).all()]

    def count_devices_by_ubication(self) -> list[tuple[str, int]]:
        stmt = (
            select(Ubication.name, func.count(Device.id))
            .join(Device, Device.ubication_id == Ubication.id, isouter=True)
            .group_by(Ubication.name)
            .order_by(Ubication.name)
        )
        return [(name or "Sin ubicación", count) for name, count in self.session.execute(stmt).all()]

    def count_devices_by_category(self) -> list[tuple[str, int]]:
        stmt = (
            select(Category.name, func.count(Device.id))
            .join(Product, Product.category_id == Category.id)
            .join(Device, Device.product_id == Product.id)
            .group_by(Category.name)
            .order_by(Category.name)
        )
        return [(name, count) for name, count in self.session.execute(stmt).all()]
    
    def list_inventory(
        self,
        status_id: int | None = None,
        ubication_id: int | None = None,
        category_id: int | None = None,
        search: str | None = None,
    ) -> Sequence[Device]:
        stmt = (
            select(Device)
            .join(Device.product)
            .outerjoin(Product.category)
            .options(
                selectinload(Device.product).selectinload(Product.category),
                selectinload(Device.status),
                selectinload(Device.ubication),
            )
            .order_by(Product.name.asc(), Device.id.asc())
        )

        if status_id is not None:
            stmt = stmt.where(Device.status_id == status_id)

        if ubication_id is not None:
            stmt = stmt.where(Device.ubication_id == ubication_id)

        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)

        if search and search.strip():
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(pattern),
                    Device.internal_code.ilike(pattern),
                    Device.serial_number.ilike(pattern),
                )
            )

        return list(self.session.execute(stmt).scalars().all())
    
    def get_devices_by_ids(self, device_ids: list[int]) -> list[Device]:
        stmt = (
            select(Device)
            .where(Device.id.in_(device_ids))
            .options(
                selectinload(Device.product).selectinload(Product.category),
                selectinload(Device.status),
                selectinload(Device.ubication),
            )
            .order_by(Device.id.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_ubication_by_id(self, ubication_id: int) -> Ubication | None:
        stmt = select(Ubication).where(Ubication.id == ubication_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add_administrative_document(self, document: AdministrativeDocument) -> AdministrativeDocument:
        self.session.add(document)
        self.session.flush()
        return document

    def commit(self) -> None:
        self.session.commit()
    
    def get_administrative_document_by_id(self, document_id: int) -> AdministrativeDocument | None:
        stmt = (
            select(AdministrativeDocument)
            .where(AdministrativeDocument.id == document_id)
            .options(
                selectinload(AdministrativeDocument.generated_by_user),
                selectinload(AdministrativeDocument.source_ubication),
                selectinload(AdministrativeDocument.target_ubication),
                selectinload(AdministrativeDocument.items),
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_or_create_ubication_by_name(self, name: str) -> Ubication:
        normalized = name.strip()

        stmt = select(Ubication).where(func.lower(Ubication.name) == normalized.lower())
        ubication = self.session.execute(stmt).scalar_one_or_none()

        if ubication:
            return ubication

        ubication = Ubication(
            name=normalized,
            description="Ubicación creada desde traslado administrativo",
        )
        self.session.add(ubication)
        self.session.flush()
        return ubication
    
    def get_status_by_name(self, status_name: str) -> Status | None:
        stmt = select(Status).where(func.lower(Status.name) == status_name.lower())
        return self.session.execute(stmt).scalar_one_or_none()
    
    def list_devices_in_maintenance(self) -> list[tuple[Device, datetime | None]]:
        maintenance_status = self.get_status_by_name("en_mantenimiento")
        if not maintenance_status:
            return []

        maintenance_since_subquery = (
            select(func.max(DeviceStatusLog.timestamp))
            .where(
                DeviceStatusLog.device_id == Device.id,
                DeviceStatusLog.status_id == maintenance_status.id,
            )
            .correlate(Device)
            .scalar_subquery()
        )

        stmt = (
            select(Device, maintenance_since_subquery.label("maintenance_since"))
            .options(
                selectinload(Device.product).selectinload(Product.category),
                selectinload(Device.status),
                selectinload(Device.ubication),
            )
            .where(Device.status_id == maintenance_status.id)
            .order_by(Device.id.asc())
        )

        return list(self.session.execute(stmt).all())

    def list_overdue_loans(self) -> list[LoanRequest]:
        borrowed_status = self.get_status_by_name("prestado")
        if not borrowed_status:
            return []

        now = datetime.now(timezone.utc)

        stmt = (
            select(LoanRequest)
            .options(
                selectinload(LoanRequest.user),
                selectinload(LoanRequest.status),
                selectinload(LoanRequest.loan_request_items)
                    .selectinload(LoanRequestItem.device)
                    .selectinload(Device.product),
            )
            .where(
                LoanRequest.status_id == borrowed_status.id,
                LoanRequest.actual_return_date.is_(None),
                LoanRequest.estimated_return_date.is_not(None),
                LoanRequest.estimated_return_date < now,
            )
            .order_by(LoanRequest.estimated_return_date.asc())
        )

        return list(self.session.execute(stmt).scalars().all())
    
    def get_status_by_id(self, status_id: int) -> Status | None:
        stmt = select(Status).where(Status.id == status_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_category_by_id(self, category_id: int) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def list_administrative_documents(self) -> list[AdministrativeDocument]:
        stmt = (
            select(AdministrativeDocument)
            .options(
                selectinload(AdministrativeDocument.generated_by_user),
                selectinload(AdministrativeDocument.source_ubication),
                selectinload(AdministrativeDocument.target_ubication),
                selectinload(AdministrativeDocument.items),
            )
            .order_by(AdministrativeDocument.generated_at.desc(), AdministrativeDocument.id.desc())
        )
        return list(self.session.execute(stmt).scalars().all())