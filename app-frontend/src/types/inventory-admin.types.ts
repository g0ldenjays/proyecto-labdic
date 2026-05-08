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

export interface InventoryTransferPayload {
  deviceIds: number[]
  targetUbicationName: string
  reason?: string | null
  observations?: string | null
}

export interface InventoryTransferResult {
  documentId: number
  updatedDevices: number
}

export interface InventoryWriteoffPayload {
  deviceIds: number[]
  reason?: string | null
  observations?: string | null
}

export interface InventoryWriteoffResult {
  documentId: number
  updatedDevices: number
}