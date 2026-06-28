// src/types/user.types.ts
import type { Role } from './role.types'

export interface User {
  id: number
  username: string
  rut: string
  name: string
  email: string
  phone: string
  address: string
  createdAt: string
  isAdmin: boolean
  isActive: boolean
  roles: Role[]
  avatarUrl?: string | null
}

export interface NewUserPayload {
  username: string
  rut: string
  name: string
  email: string
  phone: string
  address: string
  password: string
  isAdmin: boolean
  roleIds?: number[]
  // Campo interno usado por mapUserPayload para enviar roles con nombre al backend
  rolesData?: { id: number; name: string }[]
}

export type UpdateUserPayload = Partial<NewUserPayload>
