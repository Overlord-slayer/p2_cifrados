// src/types.ts

/**
 * Representa un mensaje P2P tal como viene del backend.
 */
export interface MessageResponse {
  sender: string
  receiver: string
  message: string
  signature?: string
  hash: string
  timestamp: string  // ISO string, p.ej. "2025-05-21T17:32:00.000Z"
}
