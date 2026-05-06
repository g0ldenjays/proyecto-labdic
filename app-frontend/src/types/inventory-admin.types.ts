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

export interface InventoryAdminFilters {
  search?: string
  statusId?: number | null
  ubicationId?: number | null
  categoryId?: number | null
}