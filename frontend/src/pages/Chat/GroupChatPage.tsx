// src/pages/chat/ChatPage.tsx

import React, { useEffect, useState } from 'react'
import GroupMessageBubble from '../../components/chat/GroupMessageBubble'
import SignToggle from '../../components/chat/SignToggle'
import MessageInput from '../../components/chat/MessageInput'
import api from '../../lib/api'
import { useAuth } from '../../store/useAuth'
import { useChatStore } from '../../store/chatStore'
import './GroupChat.css'
import { HiUsers, HiOutlineUsers } from 'react-icons/hi'
import { getUsername } from '@store/userStore'

export default function GroupChatPage() {
	const me = useAuth(state => state.accessToken)!

	const [contacts, setContacts] = useState<{ id: string }[]>([])
	const [active, setActive] = useState<string>('')
	const [sign, setSign] = useState<boolean>(false)

	const messages = useChatStore(state => state.messages)
	const setMessages = useChatStore(state => state.setMessages)

	const [showModal, setShowModal] = useState(false);
	const [groupName, setGroupName] = useState('');

	const handleSend = async () => {
		try {
			await api.post('/group-messages/create', {
				name : groupName
			}, {
				headers: {
					Authorization: `Bearer ${me}`
				}
			}).then(res =>
				api.post(`/group-messages/${res.data}/add`, {
					name : getUsername()
				}, {
					headers: {
						Authorization: `Bearer ${me}`
					}
				})
			)
		} catch (err) {
			console.error('Error creating group:', err)
		}
	};

	useEffect(() => {
		api.get(`/users/${getUsername()}/groups`, {
			headers: {
				Authorization: `Bearer ${me}`
			}
		})
		.then(res => setContacts(res.data))
		.catch(err => console.error('Error fetching groups:', err))
	}, [])

	useEffect(() => {
		if (!active) return
		api.get(`/group-messages/${active}`, {
			headers: {
				Authorization: `Bearer ${me}`
			}
		})
		.then(res => setMessages(res.data))
		.catch(err => console.error('Error fetching messages:', err))
	}, [active, me, setMessages])

	const send = async (text: string) => {
		try {
			await api.post(`/group-messages/${active}`, {
				message: text,
				signed: sign
			}, {
				headers: {
					Authorization: `Bearer ${me}`
				}
			})
			const res = await api.get(`/group-messages/${active}`, {
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
			<aside className="sidebar">
				<button onClick={() => setShowModal(true)}>
				Create Group
				</button>
				{showModal && (
					<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
					<div className="bg-white p-6 rounded-lg shadow-md w-80">
						<h2 className="text-lg font-semibold mb-4">Enter Group Name</h2>
						<input
						type="text"
						value={groupName}
						onChange={(e) => setGroupName(e.target.value)}
						className="w-full px-3 py-2 border rounded mb-4"
						placeholder="Group Name"
						/>
						<div className="flex justify-end gap-2">
						<button
							onClick={() => setShowModal(false)}
							className="px-4 py-2 text-gray-700 border rounded hover:bg-gray-100"
						>
							Cancel
						</button>
						<button
							onClick={handleSend}
							className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
							disabled={!groupName.trim()}
						>
							Confirm
						</button>
						</div>
					</div>
					</div>
				)}

				<h2 className="sidebar-title">
					<HiUsers className="sidebar-icon" />
					Groups
				</h2>
				<div className="contact-list">
					{contacts.map(c => {
						const isActive = c.id === active
						const Icon = HiOutlineUsers

						return (
							<div
								key={c.id}
								className={`contact-item ${isActive ? 'active' : ''}`}
								onClick={() => setActive(c.id)}
							>
								<Icon className="contact-icon" />
								<span className="contact-label">{c.id}</span>
							</div>
						)
					})}
				</div>
			</aside>

			<div className="chat-panel">
				<header className="chat-header">
				<span>{active ? `🔒 ${active}` : 'Selecciona un contacto'}</span>
				</header>

				{active && (
					<>
						<main className="chat-messages">
							{messages.map(msg => (
								<GroupMessageBubble
									key={`${msg.timestamp}-${msg.sender}`}
									msg={msg}
									me={msg.sender == getUsername()}
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