// src/pages/chat/ChatPage.tsx

import React, { useEffect, useState } from 'react'
import Sidebar from '../../components/layout/Sidebar'
import MessageBubble from '../../components/chat/MessageBubble'
import SignToggle from '../../components/chat/SignToggle'
import MessageInput from '../../components/chat/MessageInput'
import api from '../../lib/api'
import { useAuth } from '../../store/useAuth'
import { useChatStore } from '../../store/chatStore'

export default function ChatPage() {
  // “me” es tu propio identificador (token/email) que obtienes del store
  const me = useAuth(state => state.accessToken)!
  const [contacts, setContacts] = useState<{ email: string }[]>([])
  const [active, setActive]     = useState<string>('')
  const [sign, setSign]         = useState<boolean>(false)

  // Zustand store para mensajes
  const messages    = useChatStore(state => state.messages)
  const setMessages = useChatStore(state => state.setMessages)

  // 1) Carga lista de usuarios/contactos
  useEffect(() => {
    api.get('/users')
       .then(res => setContacts(res.data))
       .catch(err => console.error('Error fetching users:', err))
  }, [])

  // 2) Carga mensajes cuando cambias de contacto
  useEffect(() => {
    if (!active) return
    api.get(`/messages/${me}/${active}`)
       .then(res => setMessages(res.data))
       .catch(err => console.error('Error fetching messages:', err))
  }, [active, me, setMessages])

  // 3) Función para enviar mensaje (y opcionalmente firmarlo)
  const send = async (text: string) => {
    try {
      await api.post(`/messages/${active}`, { message: text, sign })
      const res = await api.get(`/messages/${me}/${active}`)
      setMessages(res.data)
    } catch (err) {
      console.error('Error sending message:', err)
    }
  }

  return (
    <div className="flex h-screen">
      {/* Sidebar de contactos */}
      <Sidebar 
        contacts={contacts} 
        active={active} 
        onSelect={setActive} 
      />

      {/* Panel principal de chat */}
      <div className="flex-1 flex flex-col bg-gray-900 text-white">
        <header className="p-4 text-2xl">
          {active ? `Chat con ${active}` : 'Selecciona un contacto'}
        </header>

        <main className="flex-1 overflow-auto p-4">
          {messages.map(msg => (
            <MessageBubble
              key={`${msg.timestamp}-${msg.sender_id}`}
              msg={msg}
              me={msg.sender_id !== Number(active)}
            />
          ))}
        </main>

        {/* Toggle para activar/desactivar firma */}
        <SignToggle enabled={sign} onToggle={setSign} />

        {/* Input para escribir y enviar nuevos mensajes */}
        <MessageInput onSend={send} />
      </div>
    </div>
  )
}
