// src/types.ts

/**
 * Representa un mensaje P2P tal como viene del backend.
 */
export interface MessageResponse {
  sender_id: number
  receiver_id: number
  message: string
  signature?: string
  timestamp: string  // ISO string, p.ej. "2025-05-21T17:32:00.000Z"
}
