from sqlalchemy.orm import Session

from .dtos import InventoryCountItem, InventoryDashboardDTO
from .repositories import InventoryAdminRepository

class InventoryAdminService:
    def __init__(self, session: Session) -> None:
        self.repository = InventoryAdminRepository(session)

    def get_dashboard(self) -> InventoryDashboardDTO:
        total_devices = self.repository.count_total_devices()

        by_status = [
            InventoryCountItem(label=name, count=count)
            for name, count in self.repository.count_devices_by_status()
        ]

        by_ubication = [
            InventoryCountItem(label=name, count=count)
            for name, count in self.repository.count_devices_by_ubication()
        ]

        by_category = [
            InventoryCountItem(label=name, count=count)
            for name, count in self.repository.count_devices_by_category()
        ]

        return InventoryDashboardDTO(
            total_devices=total_devices,
            by_status=by_status,
            by_ubication=by_ubication,
            by_category=by_category,
        )