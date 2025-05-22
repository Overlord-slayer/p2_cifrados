// src/pages/chat/ChatPage.tsx

import React, { useEffect, useState } from 'react'
import Sidebar from '../../components/layout/Sidebar'
import MessageBubble from '../../components/chat/MessageBubble'
import SignToggle from '../../components/chat/SignToggle'
import MessageInput from '../../components/chat/MessageInput'
import api from '../../lib/api'
import { useAuth } from '../../store/useAuth'
import { useChatStore } from '../../store/chatStore'
import './ChatPage.css'

export default function ChatPage() {
	const me = useAuth(state => state.accessToken)!
	const [contacts, setContacts] = useState<{ email: string }[]>([])
	const [active, setActive] = useState<string>('')
	const [sign, setSign] = useState<boolean>(false)
	const [is_group, setIsGroup] = useState<boolean>(false)

	const messages = useChatStore(state => state.messages)
	const setMessages = useChatStore(state => state.setMessages)

	useEffect(() => {
		api.get('/users', {
			headers: {
				Authorization: `Bearer ${me}`
			}
		})
		.then(res => setContacts(res.data))
		.catch(err => console.error('Error fetching users:', err))
	}, [])

	useEffect(() => {
		if (!active) return
		api.get(`/messages/${me}/${active}`, {
			headers: {
				Authorization: `Bearer ${me}`
			}
		})
		.then(res => setMessages(res.data))
		.catch(err => console.error('Error fetching messages:', err))
	}, [active, me, setMessages])

	const send = async (text: string) => {
		try {
			await api.post(`/messages/${active}`, {
				message: text,
				signed: sign
			}, {
				headers: {
					Authorization: `Bearer ${me}`
				}
			})
			const res = await api.get(`/messages/${me}/${active}`, {
				headers: {
					Authorization: `Bearer ${me}`
				}
			})
			setMessages(res.data)
		} catch (err) {
			console.error('Error sending message:', err)
		}
	}

	return (
		<div className="chat-container">
			<aside className="chat-sidebar">
				<Sidebar contacts={contacts} active={active} onSelect={setActive} />
			</aside>

			<div className="chat-panel">
				<header className="chat-header">
				<span>{active ? `🔒 ${active}` : 'Selecciona un contacto'}</span>
				</header>

				{active && (
					<>
						<main className="chat-messages">
							{messages.map(msg => (
								<MessageBubble
								key={`${msg.timestamp}-${msg.sender_id}`}
								msg={msg}
								me={msg.sender_id !== Number(active)}
								/>
							))}
						</main>

						<div className="chat-footer">
							<SignToggle enabled={sign} onToggle={setSign} />
							<MessageInput onSend={send} />
						</div>
					</>
				)}
			</div>
		</div>
	)
}