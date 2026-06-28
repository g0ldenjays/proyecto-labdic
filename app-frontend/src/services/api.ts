// src/api/index.ts
import * as changeKeys from 'change-case/keys'

import { useAuthStore } from "../stores/auth.store"
import { useUserStore } from '../stores/user.store'
import { useRouter } from 'vue-router'

export const BASE_URL = import.meta.env.VITE_API_URL

interface RequestInitWithJson extends RequestInit {
  json?: object | null | undefined
}


/**
 * Función genérica para hacer peticiones a la API que configura automáticamente
 * el encabezado Authorization usando el token actual del store de auth.
 * También maneja el parseo JSON y el tratamiento básico de errores.
 *
 * @template T El tipo esperado de la respuesta
 * @param url La URL relativa del endpoint de la API
 * @param options Opciones adicionales para fetch como method, headers o body
 * @returns La respuesta parseada en JSON
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInitWithJson = {},
): Promise<T> {
  const auth = useAuthStore()
  const user = useUserStore()
  const router = useRouter()

  let headers = options.headers || {}

  if (auth.isAuthenticated) {
    headers = {
      Authorization: `Bearer ${auth.token}`,
      ...headers
    }
  }

  if (options.json) {
    options.body = JSON.stringify(changeKeys.snakeCase(options.json, 5))
    options.json = undefined

    headers = {
      'Content-Type': 'application/json',
      ...headers,
    }
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: headers,
  })

  if (!response.ok) {
    if (response.status === 401) {
      auth.clearToken()
      user.clearUser()

      router.push({ name: 'login', query: { expiredToken: "true" } })
    }

    throw new Error(`HTTP error! status: ${response.status}`)
  }

  // 204 No Content by DELETE.
  if (response.status === 204) {
    return undefined as T
  }

  // También puede haber 200 con cuerpo vacío, así que leemos como texto
  const text = await response.text()

  if (!text) {
    // cuerpo vacío, nada que parsear
    return undefined as T
  }

  // Si hay texto, asumimos JSON
  const rawJson = JSON.parse(text)
  const jsonResponse = changeKeys.camelCase(rawJson, 5) as T
  //console.log('apiFetch response:', jsonResponse)
  return jsonResponse
}

export async function apiDownload(
  endpoint: string,
  filename: string,
  options: RequestInit = {},
): Promise<void> {
  const auth = useAuthStore()
  const user = useUserStore()
  const router = useRouter()

  let headers = options.headers || {}

  if (auth.isAuthenticated) {
    headers = {
      Authorization: `Bearer ${auth.token}`,
      ...headers,
    }
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    if (response.status === 401) {
      auth.clearToken()
      user.clearUser()
      router.push({ name: 'login', query: { expiredToken: 'true' } })
    }

    throw new Error(`HTTP error! status: ${response.status}`)
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}
