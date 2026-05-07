from litestar import Controller, Response, get, post, Request
from litestar.exceptions import ClientException
from litestar.di import Provide
from litestar.params import Parameter
from sqlalchemy.orm import Session

from .dtos import InventoryDashboardDTO, InventoryTransferCreateDTO, InventoryTransferResultDTO
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
    
    @get("/export/xlsx", summary="ExportInventoryAdminXlsx")
    async def export_inventory_xlsx(
        self,
        inventory_admin_service: InventoryAdminService,
        status_id: Optional[int] = Parameter(query="status_id", default=None, required=False),
        ubication_id: Optional[int] = Parameter(query="ubication_id", default=None, required=False),
        category_id: Optional[int] = Parameter(query="category_id", default=None, required=False),
        search: Optional[str] = Parameter(query="search", default=None, required=False),
    ) -> Response[bytes]:
        content = inventory_admin_service.export_inventory_xlsx(
            status_id=status_id,
            ubication_id=ubication_id,
            category_id=category_id,
            search=search,
        )

        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": 'attachment; filename="inventario_admin.xlsx"'
            },
        )
    
    @post("/documents/transfer", summary="CreateInventoryTransferDocument")
    async def create_transfer_document(
        self,
        data: InventoryTransferCreateDTO,
        request: Request,
        inventory_admin_service: InventoryAdminService,
    ) -> InventoryTransferResultDTO:
        try:
            return inventory_admin_service.create_transfer_document(
                data=data,
                generated_by_user_id=request.user.id,
            )
        except ValueError as exc:
            raise ClientException(str(exc)) from exc
        
    @get("/documents/{document_id:int}/transfer/pdf", summary="DownloadTransferPdf")
    async def download_transfer_pdf(
        self,
        document_id: int,
        inventory_admin_service: InventoryAdminService,
    ) -> Response[bytes]:
        try:
            pdf_bytes = inventory_admin_service.generate_transfer_pdf(document_id)
        except ValueError as exc:
            raise ClientException(str(exc)) from exc

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="traslado_{document_id}.pdf"'
            },
        )