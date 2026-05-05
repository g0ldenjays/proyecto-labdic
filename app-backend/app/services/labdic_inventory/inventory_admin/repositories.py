from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.inventory import Category, Device, Product, Status, Ubication


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