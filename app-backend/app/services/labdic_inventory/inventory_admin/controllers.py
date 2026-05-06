from litestar import Controller, get
from litestar.di import Provide
from litestar.params import Parameter
from sqlalchemy.orm import Session

from .dtos import InventoryDashboardDTO
from .services import InventoryAdminService
from app.models.inventory import Device
from app.services.labdic_inventory.device.dtos import DeviceReadDTO

from typing import Optional, Sequence


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
    
    @get("/inventory", summary="ListInventoryAdminDevices", return_dto=DeviceReadDTO)
    async def list_inventory(
        self,
        inventory_admin_service: InventoryAdminService,
        status_id: Optional[int] = Parameter(query="status_id", default=None, required=False),
        ubication_id: Optional[int] = Parameter(query="ubication_id", default=None, required=False),
        category_id: Optional[int] = Parameter(query="category_id", default=None, required=False),
        search: Optional[str] = Parameter(query="search", default=None, required=False),
    ) -> Sequence[Device]:
        return inventory_admin_service.list_inventory(
            status_id=status_id,
            ubication_id=ubication_id,
            category_id=category_id,
            search=search,
        )