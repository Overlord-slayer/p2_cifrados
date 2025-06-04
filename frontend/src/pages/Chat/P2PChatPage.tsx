// src/pages/chat/ChatPage.tsx

import React, { useEffect, useState } from 'react'
import Sidebar from '../../components/layout/Sidebar'
import MessageBubble from '../../components/chat/MessageBubble'
import SignToggle from '../../components/chat/SignToggle'
import MessageInput from '../../components/chat/MessageInput'
import api from '../../lib/api'
import { useAuth } from '../../store/useAuth'
import { useChatStore } from '../../store/chatStore'
import './P2PChat.css'
import { getUsername, getPublicKey, loadUsername, loadPublicKey } from '@store/userStore'

export default function ChatPage() {
	const me = useAuth(state => state.accessToken)!

	const [contacts, setContacts] = useState<{ id: string }[]>([])
	const [active, setActive] = useState<string>('')
	const [sign, setSign] = useState<boolean>(false)

	const messages = useChatStore(state => state.messages)
	const setMessages = useChatStore(state => state.setMessages)

	useEffect(() => {
		if (getUsername().length === 0) {
			loadUsername(me)
		}
		if (getPublicKey().length === 0) {
			loadPublicKey(getUsername(), me)
		}
	}, [])

	useEffect(() => {
		api.get('/users', {
			headers: {
				Authorization: `Bearer ${me}`
			}
		})
			.then(res => setContacts(res.data))
			.catch(err => console.error('Error fetching users:', err))
		console.log(getUsername())
	}, [])

	useEffect(() => {
		if (!active) return
		api.get(`/messages/${getUsername()}/${active}`, {
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
			const res = await api.get(`/messages/${getUsername()}/${active}`, {
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
				<Sidebar contacts={contacts} username={getUsername()} active={active} onSelect={setActive} />
			</aside>

			<div className="chat-panel">
				<header className="chat-header">
					<span>{active ? `${active}` : 'Selecciona un contacto'}</span>
				</header>

				{active && (
					<>
						<div className="chat-messages">
							{messages.slice().map(msg => (
								<MessageBubble
									key={`${msg.timestamp}-${msg.sender}`}
									msg={msg}
									me={msg.sender == getUsername()}
								/>
							))}
						</div>

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
