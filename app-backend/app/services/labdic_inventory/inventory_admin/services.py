from sqlalchemy.orm import Session
from .dtos import InventoryCountItem, InventoryDashboardDTO, InventoryTransferCreateDTO, InventoryTransferResultDTO
from .repositories import InventoryAdminRepository
from collections.abc import Sequence
from app.models.inventory import Device, AdministrativeDocument, AdministrativeDocumentItem
from .exporters import build_inventory_xlsx
from .documents import build_transfer_pdf

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
    
    def list_inventory(
        self,
        status_id: int | None = None,
        ubication_id: int | None = None,
        category_id: int | None = None,
        search: str | None = None,
    ) -> Sequence[Device]:
        return self.repository.list_inventory(
            status_id=status_id,
            ubication_id=ubication_id,
            category_id=category_id,
            search=search,
        )
    
    def export_inventory_xlsx(
        self,
        status_id: int | None = None,
        ubication_id: int | None = None,
        category_id: int | None = None,
        search: str | None = None,
    ) -> bytes:
        devices = self.repository.list_inventory(
            status_id=status_id,
            ubication_id=ubication_id,
            category_id=category_id,
            search=search,
        )
        return build_inventory_xlsx(devices)
    
    def create_transfer_document(
        self,
        data: InventoryTransferCreateDTO,
        generated_by_user_id: int,
    ) -> InventoryTransferResultDTO:
        device_ids = list(dict.fromkeys(data.device_ids))

        if not device_ids:
            raise ValueError("Debes seleccionar al menos un dispositivo.")

        devices = self.repository.get_devices_by_ids(device_ids)
        if len(devices) != len(device_ids):
            raise ValueError("Uno o más dispositivos no existen.")

        target_name = data.target_ubication_name.strip()
        if not target_name:
            raise ValueError("La ubicación destino es obligatoria.")

        target_ubication = self.repository.get_or_create_ubication_by_name(target_name)

        unique_source_ids = {device.ubication_id for device in devices if device.ubication_id is not None}
        source_ubication_id = next(iter(unique_source_ids)) if len(unique_source_ids) == 1 else None

        snapshot = {
            "target_ubication": {
                "id": target_ubication.id,
                "name": target_ubication.name,
            },
            "devices": [
                {
                    "id": device.id,
                    "product": device.product.name if device.product else None,
                    "internal_code": device.internal_code,
                    "serial_number": device.serial_number,
                    "status": device.status.name if device.status else None,
                    "source_ubication": device.ubication.name if device.ubication else None,
                }
                for device in devices
            ],
        }

        document = AdministrativeDocument(
            document_type="transfer",
            generated_by_user_id=generated_by_user_id,
            reason=data.reason,
            observations=data.observations,
            source_ubication_id=source_ubication_id,
            target_ubication_id=target_ubication.id,
            snapshot=snapshot,
            items=[
                AdministrativeDocumentItem(device_id=device.id)
                for device in devices
            ],
        )

        self.repository.add_administrative_document(document)

        for device in devices:
            device.ubication_id = target_ubication.id

        self.repository.commit()

        return InventoryTransferResultDTO(
            document_id=document.id,
            updated_devices=len(devices),
        )
    
    def generate_transfer_pdf(self, document_id: int) -> bytes:
        document = self.repository.get_administrative_document_by_id(document_id)

        if not document:
            raise ValueError("El documento administrativo no existe.")

        if document.document_type != "transfer":
            raise ValueError("El documento indicado no corresponde a un traslado.")

        return build_transfer_pdf(document)