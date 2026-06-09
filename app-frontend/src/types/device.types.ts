// src/types/device.types.ts
import type { Product } from './product.types'
import type { Status, Ubication } from './catalog.types'

export interface Device {
  id: number
  product: Product
  productId: number
  internalCode?: string
  serialNumber?: string
  status: Status
  statusId: number
  ubication?: Ubication
  ubicationId?: number
  createdAt: string
  observation?: string | null
}

export interface DevicePayload {
  productId: number
  statusId: number
  internalCode?: string | null
  serialNumber?: string | null
  ubicationId?: number | null
  observation?: string | null
}

export interface DeviceStatusLog {
  id: number
  deviceId: number
  status: Status
  timestamp: string
  user: { id: number; username: string; name: string }
}
