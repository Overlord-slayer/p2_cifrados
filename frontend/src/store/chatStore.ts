// src/store/chatStore.ts
import { create } from 'zustand'

import { MessageResponse } from '../types'

interface ChatState {
  messages: MessageResponse[]
  setMessages: (msgs: MessageResponse[]) => void
}

export const useChatStore = create<ChatState>(set => ({
  // Estado inicial: lista vacía de mensajes
  messages: [],
  // Acción para actualizar los mensajes
  setMessages: msgs => set({ messages: msgs }),
}))
