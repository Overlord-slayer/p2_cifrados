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
	const [availableUsers, setAvailableUsers] = useState<{ email: string }[]>([])
	const [selectedUser, setSelectedUser] = useState<string>('')

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
				}).then(temp =>
					api.get(`/users/${getUsername()}/groups`, {
						headers: {
							Authorization: `Bearer ${me}`
						}
					})
					.then(res2 => setContacts(res2.data))
					.catch(err => console.error('Error fetching groups:', err))
				)
			)
		} catch (err) {
			console.error('Error creating group:', err)
		}
	};

	const handleAddUser = async () => {
		try {
			await api.post(`/group-messages/${active}/add`, {
				name: selectedUser
			}, {
				headers: {
					Authorization: `Bearer ${me}`
				}
			})
			alert(`✅ ${selectedUser} agregado al grupo`)
			setSelectedUser('')
		} catch (err) {
			console.error('Error adding user to group:', err)
			alert('No se pudo agregar el usuario')
		}
	}

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
		api.get('/users', {
			headers: {
				Authorization: `Bearer ${me}`
			}
		})
		.then(res => setAvailableUsers(res.data))
		.catch(err => console.error('Error fetching users:', err))
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
				signed: false
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
			<aside className="sidebar p-4 text-white">
				<button
					onClick={() => setShowModal(true)}
					className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded mb-4 text-sm font-medium"
				>
					+ Crear Grupo
				</button>

				{showModal && (
					<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
						<div className="bg-white p-6 rounded-lg shadow-md w-96">
							<h2 className="text-xl font-semibold mb-4 text-gray-800">Nuevo Grupo</h2>
							<input
								type="text"
								value={groupName}
								onChange={(e) => setGroupName(e.target.value)}
								className="w-full px-3 py-2 border rounded mb-4"
								placeholder="Nombre del grupo"
							/>
							<div className="flex justify-end gap-2">
								<button
									onClick={() => setShowModal(false)}
									className="px-4 py-2 text-gray-700 border rounded hover:bg-gray-100"
								>
									Cancelar
								</button>
								<button
									onClick={handleSend}
									className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
									disabled={!groupName.trim()}
								>
									Crear
								</button>
							</div>
						</div>
					</div>
				)}

				<h2 className="sidebar-title text-lg font-bold mb-3 flex items-center gap-2">
					<HiUsers className="text-xl" />
					<span>Grupos</span>
				</h2>

				<div className="contact-list space-y-2">
					{contacts.map(c => {
						const isActive = c.id === active
						const Icon = HiOutlineUsers
						return (
							<div
								key={c.id}
								className={`contact-item px-3 py-2 rounded cursor-pointer flex items-center gap-2 ${isActive ? 'bg-blue-700' : 'hover:bg-gray-800'}`}
								onClick={() => setActive(c.id)}
							>
								<Icon className="text-lg" />
								<span>{c.id}</span>
							</div>
						)
					})}

					{!contacts.length && (
						<div className="group-add-container mt-4 text-sm">
							<p className="text-gray-400 mb-2">No hay grupos disponibles</p>
							<select
								value={selectedUser}
								onChange={(e) => setSelectedUser(e.target.value)}
								className="w-full px-3 py-2 border rounded mb-2 text-black"
							>
								<option value="">-- Selecciona usuario para agregar --</option>
								{availableUsers.map(u => (
									<option key={u.email} value={u.email}>{u.email}</option>
								))}
							</select>
							<button
								onClick={handleAddUser}
								disabled={!selectedUser}
								className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
							>
								Agregar al grupo
							</button>
						</div>
					)}
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
							<MessageInput onSend={send} />
						</div>
					</>
				)}
			</div>
		</div>
	)
}
