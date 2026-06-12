import { apiFetch } from '@/services/api'
import type { Book, BookPayload } from '@/types/book.types'

export function getBooks(): Promise<Book[]> {
  return apiFetch('/labdic_inventory/books/')
}

export function createBook(payload: BookPayload): Promise<Book> {
  return apiFetch('/labdic_inventory/books/', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateBook(id: number, payload: Partial<BookPayload>): Promise<Book> {
  return apiFetch(`labdic_inventory/books/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}