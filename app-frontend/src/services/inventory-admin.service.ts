import type { InventoryAdminFilters, InventoryDashboard } from '@/types/inventory-admin.types'
import { apiFetch } from '@/services/api'
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
