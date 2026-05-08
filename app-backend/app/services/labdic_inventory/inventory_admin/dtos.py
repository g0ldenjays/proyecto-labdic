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