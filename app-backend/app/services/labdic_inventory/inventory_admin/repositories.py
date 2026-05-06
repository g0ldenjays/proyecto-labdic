from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from app.models.inventory import Category, Device, Product, Status, Ubication
from typing import Sequence


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