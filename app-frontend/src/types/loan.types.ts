// src/types/loan.types.ts
import type { User } from './user.types'
import type { Status } from './catalog.types'
import type { Device } from './device.types'

export interface LoanRequestItem {
  id: number
  deviceId: number
  device: Device
}

export interface LoanRequest {
  id: number
  userId: number
  user: User
  status: Status
  statusId: number
  reason?: string
  additionalItems?: string
  requestDate: string
  deliveryDate?: string
  estimatedReturnDate?: string
  actualReturnDate?: string
  loanRequestItems: LoanRequestItem[]
}

export interface LoanRequestCreatePayload {
  deviceIds: number[]
  reason?: string
  estimatedReturnDate?: string
  requestedUserId?: number
  additionalItems?: string
}
