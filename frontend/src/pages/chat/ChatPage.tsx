// src/pages/Chat/ChatPage.tsx

import React, { useEffect, useState } from 'react'
import Sidebar from '../../components/layout/Sidebar'
import MessageBubble from '../../components/chat/MessageBubble'
import SignToggle from '../../components/chat/SignToggle'
import MessageInput from '../../components/chat/MessageInput'
import api from '../../lib/api'
import { useAuth } from '../../store/useAuth'
import { useChatStore } from '../../store/chatStore'

export default function ChatPage() {
  const me        = useAuth(s => s.accessToken)!
  const [contacts, setContacts] = useState<{ email: string }[]>([])
  const [active, setActive]     = useState<string>('')
  const [sign, setSign]         = useState(false)
  const messages = useChatStore(s => s.messages)
  const setMessages = useChatStore(s => s.setMessages)

  // Cargar lista de contactos
  useEffect(() => {
    api.get('/users').then(r => setContacts(r.data))
  }, [])

  // Cargar mensajes al cambiar de contacto
  useEffect(() => {
    if (!active) return
    api.get(`/messages/${me}/${active}`)
       .then(r => setMessages(r.data))
  }, [active])

  // Enviar mensaje (cifrado/firma opcional)
  const send = async (text: string) => {
    await api.post(`/messages/${active}`, { message: text, sign })
    const r = await api.get(`/messages/${me}/${active}`)
    setMessages(r.data)
  }

  return (
    <div className="flex h-screen">
      <Sidebar contacts={contacts} active={active} onSelect={setActive} />
      <div className="flex-1 flex flex-col bg-gray-900 text-white">
        <header className="p-4 text-2xl">Chat con {active}</header>
        <main className="flex-1 overflow-auto p-4">
          {messages.map(msg => (
            <MessageBubble
              key={msg.timestamp + msg.sender_id}
              msg={msg}
              me={msg.sender_id !== Number(active)}
            />
          ))}
        </main>
        <SignToggle enabled={sign} onToggle={setSign} />
        <MessageInput onSend={send} />
      </div>
    </div>
  )
}
