export interface InventoryCountItem {
  label: string
  count: number
}

export interface InventoryDashboard {
  totalDevices: number
  byStatus: InventoryCountItem[]
  byUbication: InventoryCountItem[]
  byCategory: InventoryCountItem[]
}