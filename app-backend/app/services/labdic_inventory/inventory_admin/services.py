from sqlalchemy.orm import Session
from .dtos import (
    InventoryAlertsDTO,
    InventoryCountItem,
    InventoryDashboardDTO,
    InventoryMaintenanceAlertItemDTO,
    InventoryOverdueLoanAlertItemDTO,
    InventoryOverdueLoanDeviceItemDTO,
    InventoryTransferCreateDTO,
    InventoryTransferResultDTO,
    InventoryWriteoffCreateDTO,
    InventoryWriteoffResultDTO,
)
from .repositories import InventoryAdminRepository
from collections.abc import Sequence
from app.models.inventory import Device, AdministrativeDocument, AdministrativeDocumentItem
from .exporters import build_inventory_xlsx
from .documents import build_transfer_pdf, build_writeoff_pdf
from datetime import datetime, timezone
from app.config import settings


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

        already_in_target = [device.id for device in devices if device.ubication_id == target_ubication.id]

        if already_in_target:
            raise ValueError(
                f"Los siguientes dispositivos ya están en la ubicación destino: {already_in_target}"
            )

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

    def create_writeoff_document(
        self,
        data: InventoryWriteoffCreateDTO,
        generated_by_user_id: int,
    ) -> InventoryWriteoffResultDTO:
        device_ids = list(dict.fromkeys(data.device_ids))

        if not device_ids:
            raise ValueError("Debes seleccionar al menos un dispositivo.")

        devices = self.repository.get_devices_by_ids(device_ids)
        if len(devices) != len(device_ids):
            raise ValueError("Uno o más dispositivos no existen.")

        writeoff_status = self.repository.get_status_by_name("de_baja")
        if not writeoff_status:
            raise ValueError("No existe el estado 'de_baja' en el sistema.")

        already_writeoff = [device.id for device in devices if device.status_id == writeoff_status.id]
        if already_writeoff:
            raise ValueError(
                f"Uno o más dispositivos ya están dados de baja: {already_writeoff}"
            )

        unique_source_ids = {device.ubication_id for device in devices if device.ubication_id is not None}
        source_ubication_id = next(iter(unique_source_ids)) if len(unique_source_ids) == 1 else None

        snapshot = {
            "devices": [
                {
                    "id": device.id,
                    "product": device.product.name if device.product else None,
                    "internal_code": device.internal_code,
                    "serial_number": device.serial_number,
                    "status_before": device.status.name if device.status else None,
                    "source_ubication": device.ubication.name if device.ubication else None,
                }
                for device in devices
            ],
        }

        document = AdministrativeDocument(
            document_type="writeoff",
            generated_by_user_id=generated_by_user_id,
            reason=data.reason,
            observations=data.observations,
            source_ubication_id=source_ubication_id,
            target_ubication_id=None,
            snapshot=snapshot,
            items=[
                AdministrativeDocumentItem(device_id=device.id)
                for device in devices
            ],
        )

        self.repository.add_administrative_document(document)

        for device in devices:
            device.status_id = writeoff_status.id

        self.repository.commit()

        return InventoryWriteoffResultDTO(
            document_id=document.id,
            updated_devices=len(devices),
        )
    
    def generate_writeoff_pdf(self, document_id: int) -> bytes:
        document = self.repository.get_administrative_document_by_id(document_id)

        if not document:
            raise ValueError("El documento administrativo no existe.")

        if document.document_type != "writeoff":
            raise ValueError("El documento indicado no corresponde a una baja.")

        return build_writeoff_pdf(document)
    
    @staticmethod
    def _ensure_aware(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    
    def get_alerts(self) -> InventoryAlertsDTO:
        now = datetime.now(timezone.utc)

        maintenance_alert_days = settings.maintenance_alert_days
        overdue_loan_alert_days = settings.overdue_loan_alert_days

        prolonged_maintenance: list[InventoryMaintenanceAlertItemDTO] = []
        for device, maintenance_since in self.repository.list_devices_in_maintenance():
            base_date = self._ensure_aware(maintenance_since or device.created_at)
            days_in_maintenance = max((now - base_date).days, 0)

            if days_in_maintenance >= maintenance_alert_days:
                prolonged_maintenance.append(
                    InventoryMaintenanceAlertItemDTO(
                        device_id=device.id,
                        product_name=device.product.name if device.product else "—",
                        internal_code=device.internal_code,
                        serial_number=device.serial_number,
                        ubication_name=device.ubication.name if device.ubication else None,
                        maintenance_since=base_date.isoformat(),
                        days_in_maintenance=days_in_maintenance,
                    )
                )

        overdue_loans: list[InventoryOverdueLoanAlertItemDTO] = []
        for loan in self.repository.list_overdue_loans():
            if not loan.estimated_return_date:
                continue

            estimated_return_date = self._ensure_aware(loan.estimated_return_date)
            days_overdue = max((now - estimated_return_date).days, 0)

            if days_overdue >= overdue_loan_alert_days:
                overdue_loans.append(
                    InventoryOverdueLoanAlertItemDTO(
                        loan_id=loan.id,
                        user_name=loan.user.name if loan.user else "—",
                        user_username=loan.user.username if loan.user else "—",
                        estimated_return_date=estimated_return_date.isoformat(),
                        days_overdue=days_overdue,
                        devices=[
                            InventoryOverdueLoanDeviceItemDTO(
                                device_id=item.device.id,
                                product_name=item.device.product.name if item.device and item.device.product else "—",
                                internal_code=item.device.internal_code if item.device else None,
                                serial_number=item.device.serial_number if item.device else None,
                            )
                            for item in loan.loan_request_items
                        ],
                    )
                )

        prolonged_maintenance.sort(key=lambda item: item.days_in_maintenance, reverse=True)
        overdue_loans.sort(key=lambda item: item.days_overdue, reverse=True)

        return InventoryAlertsDTO(
            maintenance_alert_days=maintenance_alert_days,
            overdue_loan_alert_days=overdue_loan_alert_days,
            prolonged_maintenance=prolonged_maintenance,
            overdue_loans=overdue_loans,
        )