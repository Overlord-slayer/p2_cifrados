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

	const [groupName, setGroupName] = useState('')
	const [showModal, setShowModal] = useState(false)
	const [iamowner, setIsOwner] = useState(false)
	const [availableUsers, setAvailableUsers] = useState<{ email: string }[]>([])
	const [selectedUser, setSelectedUser] = useState('')

	const messages = useChatStore(state => state.messages)
	const setMessages = useChatStore(state => state.setMessages)

	const createGroup = async () => {
		try {
			const res = await api.post('/group-messages/create', {
				name: groupName
			}, {
				headers: { Authorization: `Bearer ${me}` }
			})

			await api.post(`/group-messages/${res.data}/add`, {
				name: getUsername()
			}, {
				headers: { Authorization: `Bearer ${me}` }
			})

			const res2 = await api.get(`/users/${getUsername()}/groups`, {
				headers: { Authorization: `Bearer ${me}` }
			})

			setContacts(res2.data)
			setActive(res.data)
			setShowModal(false)
			setGroupName('')
		} catch (err) {
			console.error('Error creating group:', err)
		}
	}

	const handleAddUser = async () => {
		try {
			await api.post(`/group-messages/${active}/add`, {
				name: selectedUser
			}, {
				headers: { Authorization: `Bearer ${me}` }
			})
			alert(`✅ ${selectedUser} agregado al grupo`)
			api.get(`/group-messages/${active}/users`, {
				headers: { Authorization: `Bearer ${me}` }
			}).then(res => setAvailableUsers(res.data))
				.catch(err => console.error('Error fetching users:', err))
			setSelectedUser('')
		} catch (err) {
			console.error('Error adding user to group:', err)
			alert('No se pudo agregar el usuario')
		}
	}

	useEffect(() => {
		if (getUsername().length == 0) return
		api.get(`/users/${getUsername()}/groups`, {
			headers: { Authorization: `Bearer ${me}` }
		}).then(res => setContacts(res.data))
			.catch(err => console.error('Error fetching groups:', err))
	}, [])

	useEffect(() => {
		if (!active) return
		api.get(`/group-messages/${active}/owner`, {
			headers: { Authorization: `Bearer ${me}` }
		}).then(res => setIsOwner(true))
			.catch(err => console.log('Validating ownership:', err.response.data.detail))
	}, [active, iamowner])

	useEffect(() => {
		if (!active) return
		api.get(`/group-messages/${active}/users`, {
			headers: { Authorization: `Bearer ${me}` }
		}).then(res => setAvailableUsers(res.data))
			.catch(err => console.log('Fetching users:', err.response.data.detail))
	}, [active])

	useEffect(() => {
		if (!active) return
		api.get(`/group-messages/${active}`, {
			headers: { Authorization: `Bearer ${me}` }
		}).then(res => setMessages(res.data))
			.catch(err => console.error('Error fetching messages:', err))
	}, [active, me])

	const send = async (text: string) => {
		try {
			await api.post(`/group-messages/${active}`, {
				message: text,
				signed: sign
			}, {
				headers: { Authorization: `Bearer ${me}` }
			})

			const res = await api.get(`/group-messages/${active}`, {
				headers: { Authorization: `Bearer ${me}` }
			})

			setMessages(res.data)
		} catch (err) {
			console.error('Error sending message:', err)
		}
	}

	return (
		<div className="chat-container" style={{ fontFamily: "'Inter', sans-serif" }}>
			<aside className="sidebar">
				<button onClick={() => setShowModal(true)} style={{
					width: '100%',
					backgroundColor: '#25D366',
					color: 'white',
					padding: '10px',
					borderRadius: '6px',
					marginBottom: '12px',
					fontWeight: 'bold',
					boxShadow: '0 2px 6px rgba(0,0,0,0.3)',
					border: 'none',
					cursor: 'pointer'
				}}>
					+ Crear Grupo
				</button>

				{showModal && (
					<div style={{
						position: 'fixed',
						inset: 0,
						backgroundColor: 'rgba(0,0,0,0.5)',
						display: 'flex',
						justifyContent: 'center',
						alignItems: 'center',
						zIndex: 50
					}}>
						<div style={{
							backgroundColor: '#111',
							color: 'white',
							padding: '24px',
							borderRadius: '12px',
							boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
							width: '400px'
						}}>
							<h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Nuevo Grupo</h2>
							<input
								type="text"
								value={groupName}
								onChange={(e) => setGroupName(e.target.value)}
								placeholder="Nombre del grupo"
								style={{
									width: '100%',
									padding: '10px',
									borderRadius: '6px',
									marginBottom: '16px',
									backgroundColor: '#000',
									color: 'white',
									border: '1px solid #444'
								}}
							/>
							<div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
								<button onClick={() => setShowModal(false)} style={{
									padding: '8px 16px',
									color: '#ccc',
									backgroundColor: '#222',
									borderRadius: '6px',
									border: '1px solid #444',
									cursor: 'pointer'
								}}>
									Cancelar
								</button>
								<button onClick={createGroup} disabled={!groupName.trim()} style={{
									padding: '8px 16px',
									backgroundColor: '#25D366',
									color: 'white',
									borderRadius: '6px',
									border: 'none',
									cursor: groupName.trim() ? 'pointer' : 'not-allowed',
									opacity: groupName.trim() ? 1 : 0.6
								}}>
									Crear
								</button>
							</div>
						</div>
					</div>
				)}

				<h2 className="sidebar-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'white', fontSize: '16px', fontWeight: 'bold' }}>
					<HiUsers style={{ fontSize: '20px' }} />
					Grupos
				</h2>

				<div className="contact-list">
					{contacts.map(c => {
						const isActive = c.id === active
						return (
							<div key={c.id}
								onClick={() => setActive(c.id)}
								style={{
									padding: '10px',
									borderRadius: '6px',
									backgroundColor: isActive ? '#128C7E' : 'transparent',
									cursor: 'pointer',
									color: 'white',
									display: 'flex',
									alignItems: 'center',
									gap: '8px'
								}}
							>
								<HiOutlineUsers />
								<span>{c.id}</span>
							</div>
						)
					})}

					{!contacts.length && (
						<div style={{ marginTop: '20px' }}>
							<p style={{ color: '#ccc', marginBottom: '8px' }}>No hay grupos disponibles</p>
						</div>
					)}
					{active && iamowner &&(
						<div style={{ marginTop: '20px' }}>
							<select value={selectedUser}
								onChange={(e) => setSelectedUser(e.target.value)}
								style={{
									width: '100%',
									padding: '8px',
									borderRadius: '6px',
									backgroundColor: '#222',
									color: 'white',
									border: '1px solid #444'
								}}
							>
								<option value="">-- Selecciona usuario para agregar --</option>
								{availableUsers.map(u => (
									<option key={u.email} value={u.email}>{u.email}</option>
								))}
							</select>
							<button
								onClick={handleAddUser}
								disabled={!selectedUser}
								style={{
									width: '100%',
									padding: '8px',
									marginTop: '8px',
									backgroundColor: '#25D366',
									color: 'white',
									borderRadius: '6px',
									border: 'none',
									cursor: selectedUser ? 'pointer' : 'not-allowed',
									opacity: selectedUser ? 1 : 0.6
								}}
							>
								Agregar al grupo
							</button>
						</div>
					)}
				</div>
			</aside>

			<div className="chat-panel">
				<header className="chat-header">
					{active && <span>{active}</span>}
				</header>

				{active && (
					<>
						<main className="chat-messages"  style={{ display: 'flex', flexDirection: 'column-reverse', gap: '8px', overflowY: 'auto' }}>
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
