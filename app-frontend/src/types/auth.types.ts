// src/types/auth.types.ts

/**
 * Token devuelto por Litestar's OAuth2PasswordBearerAuth.
 * Solo contiene access_token y token_type — Litestar NO envía
 * expiresIn ni refreshToken por defecto.
 * TODO: refreshToken
 */
export interface Token {
  accessToken: string
  tokenType: string
}

export interface InventoryTransferPayload {
  deviceIds: number[]
  targetUbicationId: number
  reason?: string | null
  observations?: string | null
}

export interface InventoryTransferResult {
  documentId: number
  updatedDevices: number
}