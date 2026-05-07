import type { InventoryAdminFilters, InventoryDashboard, InventoryTransferPayload, InventoryTransferResult } from '@/types/inventory-admin.types'
import { apiFetch, apiDownload } from '@/services/api'
import type { Device } from '@/types/device.types'

const BASE_PATH = '/labdic_inventory/inventory-admin'

export async function getInventoryDashboard(): Promise<InventoryDashboard> {
  return apiFetch<InventoryDashboard>(`${BASE_PATH}/dashboard`)
}

export async function getInventoryDevices(filters: InventoryAdminFilters = {}): Promise<Device[]> {
  const params = new URLSearchParams()

  if (filters.search?.trim()) {
    params.set('search', filters.search.trim())
  }
  if (filters.statusId) {
    params.set('status_id', String(filters.statusId))
  }
  if (filters.ubicationId) {
    params.set('ubication_id', String(filters.ubicationId))
  } 
  if (filters.categoryId) {
    params.set('category_id', String(filters.categoryId))
  }

  const query = params.toString()
  return apiFetch<Device[]>(`${BASE_PATH}/inventory${query ? `?${query}` : ''}`)
}

export async function downloadInventoryXlsx(filters: InventoryAdminFilters = {},): Promise<void> {
  const params = new URLSearchParams()

  if (filters.search?.trim()) {
    params.set('search', filters.search.trim())
  }
  if (filters.statusId) {
    params.set('status_id', String(filters.statusId))
  }
  if (filters.ubicationId) {
    params.set('ubication_id', String(filters.ubicationId))
  }
  if (filters.categoryId) {
    params.set('category_id', String(filters.categoryId))
  }

  const query = params.toString()
  await apiDownload(
    `${BASE_PATH}/export/xlsx${query ? `?${query}` : ''}`,
    'inventario_admin.xlsx',
  )
}

export async function createInventoryTransfer(
  payload: InventoryTransferPayload,
): Promise<InventoryTransferResult> {
  return apiFetch<InventoryTransferResult>(`${BASE_PATH}/documents/transfer`, {
    method: 'POST',
    body: JSON.stringify({
      device_ids: payload.deviceIds,
      target_ubication_name: payload.targetUbicationName,
      reason: payload.reason,
      observations: payload.observations,
    }),
  })
}

export async function downloadTransferPdf(documentId: number): Promise<void> {
  await apiDownload(
    `${BASE_PATH}/documents/${documentId}/transfer/pdf`,
    `traslado_${documentId}.pdf`,
  )
}