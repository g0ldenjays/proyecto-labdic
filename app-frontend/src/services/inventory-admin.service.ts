import type { InventoryDashboard } from '@/types/inventory-admin.types'
import { apiFetch } from '@/services/api'

const BASE_PATH = '/labdic_inventory/inventory-admin'

export async function getInventoryDashboard(): Promise<InventoryDashboard> {
  return apiFetch<InventoryDashboard>(`${BASE_PATH}/dashboard`)
}