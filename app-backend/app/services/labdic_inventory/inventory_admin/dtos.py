from msgspec import Struct

class InventoryCountItem(Struct):
    label: str
    count: int

class InventoryDashboardDTO(Struct):
    total_devices: int
    by_status: list[InventoryCountItem]
    by_ubication: list[InventoryCountItem]
    by_category: list[InventoryCountItem]