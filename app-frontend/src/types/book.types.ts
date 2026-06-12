export interface Book {
  id: number
  title: string
  author?: string | null
  isbn?: string | null
  topic?: string | null
  description?: string | null
  totalQuantity: number
  availableQuantity: number
  isActive: boolean
  createdAt: string
}

export interface BookPayload {
  title: string
  author?: string | null
  isbn?: string | null
  topic?: string | null
  description?: string | null
  totalQuantity: number
  availableQuantity?: number | null
  isActive: boolean
}