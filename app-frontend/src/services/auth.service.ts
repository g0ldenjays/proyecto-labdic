// src/api/auth.ts
import type { Token } from '@/types/auth.types'
import { apiFetch } from '@/services/api'

// Base path for auth-related API endpoints
const AUTH = '/labdic_inventory/auth'

/**
 * Performs a login request with the provided credentials.
 * Returns a Token object containing the access token and expiry information.
 *
 * @param username The username or email
 * @param password The password
 * @returns A promise that resolves to a Token
 */
export async function login(
  username: string,
  password: string
): Promise<Token> {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)

  return await apiFetch(`${AUTH}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params,
  })
}

export interface GoogleRegisterPayload {
  credential: string
  password: string
  confirmPassword: string
  rut?: string | null
}

export function googleRegister(payload: GoogleRegisterPayload) {
  return apiFetch(`${AUTH}/google-register`, {
    method: 'POST',
    json: payload,
  })
}