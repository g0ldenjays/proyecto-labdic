from msgspec import Struct

class InventoryCountItem(Struct):
    label: str
    count: int

class InventoryDashboardDTO(Struct):
    total_devices: int
    by_status: list[InventoryCountItem]
    by_ubication: list[InventoryCountItem]
    by_category: list[InventoryCountItem]

class InventoryTransferCreateDTO(Struct):
    device_ids: list[int]
    target_ubication_name: str
    reason: str | None = None
    observations: str | None = None


class InventoryTransferResultDTO(Struct):
    document_id: int
    updated_devices: int

class InventoryWriteoffCreateDTO(Struct):
    device_ids: list[int]
    reason: str | None = None
    observations: str | None = None

class InventoryWriteoffResultDTO(Struct):
    document_id: int
    updated_devices: int

class InventoryMaintenanceAlertItemDTO(Struct):
    device_id: int
    product_name: str
    maintenance_since: str
    days_in_maintenance: int
    internal_code: str | None = None
    serial_number: str | None = None
    ubication_name: str | None = None

class InventoryOverdueLoanDeviceItemDTO(Struct):
    device_id: int
    product_name: str
    internal_code: str | None = None
    serial_number: str | None = None


class InventoryOverdueLoanAlertItemDTO(Struct):
    loan_id: int
    user_name: str
    user_username: str
    estimated_return_date: str
    days_overdue: int
    devices: list[InventoryOverdueLoanDeviceItemDTO]


class InventoryAlertsDTO(Struct):
    maintenance_alert_days: int
    overdue_loan_alert_days: int
    prolonged_maintenance: list[InventoryMaintenanceAlertItemDTO]
    overdue_loans: list[InventoryOverdueLoanAlertItemDTO]

class AdministrativeDocumentListItemDTO(Struct):
    id: int
    document_type: str
    generated_at: str
    generated_by_user_name: str
    items_count: int
    source_ubication_name: str | None = None
    target_ubication_name: str | None = None
    reason: str | None = None
    observations: str | None = None


class AdministrativeDocumentListDTO(Struct):
    items: list[AdministrativeDocumentListItemDTO]