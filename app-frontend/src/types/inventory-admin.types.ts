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

export interface InventoryMaintenanceAlertItem {
  deviceId: number
  productName: string
  internalCode?: string | null
  serialNumber?: string | null
  ubicationName?: string | null
  maintenanceSince: string
  daysInMaintenance: number
}

export interface InventoryOverdueLoanDeviceItem {
  deviceId: number
  productName: string
  internalCode?: string | null
  serialNumber?: string | null
}

export interface InventoryOverdueLoanAlertItem {
  loanId: number
  userName: string
  userUsername: string
  estimatedReturnDate: string
  daysOverdue: number
  devices: InventoryOverdueLoanDeviceItem[]
}

export interface InventoryAlerts {
  maintenanceAlertDays: number
  overdueLoanAlertDays: number
  prolongedMaintenance: InventoryMaintenanceAlertItem[]
  overdueLoans: InventoryOverdueLoanAlertItem[]
}

export interface AdministrativeDocumentListItem {
  id: number
  documentType: string
  generatedAt: string
  generatedByUserName: string
  sourceUbicationName?: string | null
  targetUbicationName?: string | null
  reason?: string | null
  observations?: string | null
  itemsCount: number
}

export interface AdministrativeDocumentList {
  items: AdministrativeDocumentListItem[]
}