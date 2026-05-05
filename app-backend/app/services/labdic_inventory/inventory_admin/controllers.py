from litestar import Controller, get
from litestar.di import Provide
from sqlalchemy.orm import Session

from .dtos import InventoryDashboardDTO
from .services import InventoryAdminService


def provide_inventory_admin_service(db_session: Session) -> InventoryAdminService:
    return InventoryAdminService(db_session)


class InventoryAdminController(Controller):
    path = "/inventory-admin"
    tags = ["inventory-admin"]
    dependencies = {
        "inventory_admin_service": Provide(provide_inventory_admin_service, sync_to_thread=False)
    }

    @get("/dashboard", summary="GetInventoryAdminDashboard")
    async def get_dashboard(
        self,
        inventory_admin_service: InventoryAdminService,
    ) -> InventoryDashboardDTO:
        return inventory_admin_service.get_dashboard()