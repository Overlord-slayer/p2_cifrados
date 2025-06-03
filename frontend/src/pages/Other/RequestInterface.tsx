import React, { useEffect, useState } from 'react'
import api from '../../lib/api'
import { useAuth } from '../../store/useAuth'
import './RequestInterface.css'
import { getUsername } from '@store/userStore'
import { setgroups } from 'process'

export default function RequestInterface() {
	const me = useAuth(state => state.accessToken)!
	const [activeTab, setActiveTab] = useState<'transactions-verify' | 'transactions' | 'hash-group' | 'hash-p2p'>('transactions-verify')

	const [transactions, setTransactions] = useState<any[]>([])
	const [transactions_verified, setTransactionsVerified] = useState<string>('')
	const [group_verified, setGroupVerified] = useState<string>('')
	const [p2p_verified, setP2PVerified] = useState<string>('')

	const [users, setUsers] = useState<string[]>([])
	const [groups, setGroups] = useState<string[]>([])
	
	const [selected_user1, setSelectedUser1] = useState('')
	const [selected_user2, setSelectedUser2] = useState('')
	const [selected_group, setSelectedGroup] = useState('')

	useEffect(() => {
		if (activeTab === 'transactions-verify') {
			api.get(`/verify-transactions`)
				.then(res => {
					const [isValid, message] = res.data
					setTransactionsVerified(message)
				})
				.catch(err => console.error('Error fetching transactions:', err))
		}
		else if (activeTab === 'transactions') {
			api.get(`/transactions`)
				.then(res => setTransactions(res.data))
				.catch(err => console.error('Error fetching verify-transactions:', err))
		}
		else if (activeTab === 'hash-group') {
			api.get(`/groups/all`)
				.then(res => setGroups(res.data))
				.catch(err => console.error('Error getting groups:', err))
		}
		else if (activeTab === 'hash-p2p') {
			api.get(`/users/all`)
				.then(res => setUsers(res.data))
				.catch(err => console.error('Error getting users:', err))
		}
	}, [activeTab])

	const renderTransactionsVerify = () => (
		<div className="flex flex-col space-y-6">
			{transactions_verified.length === 0 ? (
				<p>No transactions found.</p>
			) :
			<h1>{transactions_verified}</h1>}
		</div>
	)

	const renderTransactions = () => (
		<div className="flex flex-col space-y-6">
			<h1 className="text-2xl font-bold" style={{ marginBottom: 25 }}>Transactions</h1>
			{transactions.length === 0 ? (
				<p>No transactions found.</p>
			) : (
				transactions.map(tx => (
					<div key={tx.id} className="border rounded-2xl shadow-lg p-6 bg-white">
						<div className="flex flex-col space-y-2">
							<h2 className="text-xl font-semibold" style={{ marginBottom: 15, marginTop:50 }}>Block #{tx.id}</h2>
							<p style={{ marginBottom: 5 }}><strong>Hash:</strong> {tx.hash}</p>
							<p style={{ marginBottom: 5 }}><strong>Previous Hash:</strong> {tx.previous_hash}</p>
							<p style={{ marginBottom: 5 }}><strong>Timestamp:</strong> {new Date(tx.timestamp).toLocaleString()}</p>
						</div>

						<div className="mt-4">
							<h3 className="font-semibold text-lg mb-2" style={{ marginBottom: 10 }}>Messages</h3>
							<div className="flex flex-col space-y-4 border-l-2 pl-4">
								{tx.messages.map((msg: any, index: number) => (
									<div key={index} className="bg-gray-50 p-3 rounded-md shadow-sm">
										<p style={{ marginBottom: 5 }}><strong>P2P:</strong> {msg.is_p2p ? 'Yes' : 'No'}</p>
										<p style={{ marginBottom: 5 }}><strong>Message ID:</strong> {msg.message_id}</p>
										<p style={{ marginBottom: 5 }}><strong>Message:</strong> {msg.message}</p>
										<p style={{ marginBottom: 5 }}><strong>Message Hash:</strong> {msg.message_hash}</p>
									</div>
								))}
							</div>
						</div>
					</div>
				))
			)}
		</div>
	)

	const handleSubmitGroup = async () => {
		api.get(`/group-messages/${selected_group}/verify-hash`)
			.then(res => {
				const [isValid, message] = res.data
				setGroupVerified(message)
			})
			.catch(err => console.error('Error fetching transactions:', err))
	}
	const renderHashGroup = () => (
		<div className="flex flex-col space-y-6 container">
			<select value={selected_group}
				onChange={(e) => setSelectedGroup(e.target.value)}
				style={{
					width: '100%',
					padding: '8px',
					borderRadius: '6px',
					backgroundColor: '#222',
					color: 'white',
					border: '1px solid #444',
					cursor: 'pointer'
				}}
			>
				{!selected_group && (
					<option value="" disabled>
					Selecciona grupo
					</option>
				)}
				{groups.map(u => (
					<option key={u} value={u}>{u}</option>
				))}
			</select>
			<button
				onClick={handleSubmitGroup}
				style={{
					width: '100%',
					padding: '8px',
					marginTop: '8px',
					backgroundColor: '#25D366',
					color: 'white',
					borderRadius: '6px',
					border: 'none',
					cursor: 'pointer'
				}}
			>
				Verificar
			</button>
			<h1>{group_verified}</h1>
		</div>
	)

	const handleSubmitP2P = async () => {
		api.get(`/messages/${selected_user1}/${selected_user2}/verify-hash`)
			.then(res => {
				const [isValid, message] = res.data
				setP2PVerified(message)
			})
			.catch(err => console.error('Error fetching transactions:', err))
	}
	const renderHashP2P = () => (
		<div className="flex flex-col space-y-6 container">
			<select value={selected_user1}
				onChange={(e) => setSelectedUser1(e.target.value)}
				style={{
					width: '100%',
					padding: '8px',
					borderRadius: '6px',
					backgroundColor: '#222',
					color: 'white',
					border: '1px solid #444',
					cursor: 'pointer'
				}}
			>
				{!selected_user1 && (
					<option value="" disabled>
					Selecciona usuario 1
					</option>
				)}
				{users.map(u => (
					<option key={u} value={u}>{u}</option>
				))}
			</select>
			<select value={selected_user2}
				onChange={(e) => setSelectedUser2(e.target.value)}
				style={{
					width: '100%',
					padding: '8px',
					borderRadius: '6px',
					backgroundColor: '#222',
					color: 'white',
					border: '1px solid #444',
					cursor: 'pointer'
				}}
			>
				{!selected_user2 && (
					<option value="" disabled>
					Selecciona usuario 2
					</option>
				)}
				{users.map(u => (
					<option key={u} value={u}>{u}</option>
				))}
			</select>
			<button
				onClick={handleSubmitP2P}
				style={{
					width: '100%',
					padding: '8px',
					marginTop: '8px',
					backgroundColor: '#25D366',
					color: 'white',
					borderRadius: '6px',
					border: 'none',
					cursor: 'pointer'
				}}
			>
				Verificar
			</button>
			<h1>{p2p_verified}</h1>
		</div>
	)

	return (
		<div className="flex flex-col space-y-6 container">
			<div className="flex flex-col space-y-6" style={{ display: "flex", justifyContent:"center"}}>
				<button
					className={`${activeTab === 'transactions-verify' ? 'item active' : 'item'}`}
					onClick={() => setActiveTab('transactions-verify')}
				>
					Verify Transactions
				</button>
				<button
					className={`${activeTab === 'transactions' ? 'item active' : 'item'}`}
					onClick={() => setActiveTab('transactions')}
				>
					Get Transactions
				</button>
				<button
					className={`${activeTab === 'hash-group' ? 'item active' : 'item'}`}
					onClick={() => setActiveTab('hash-group')}
				>
					Hash Group
				</button>
				<button
					className={`${activeTab === 'hash-p2p' ? 'item active' : 'item'}`}
					onClick={() => setActiveTab('hash-p2p')}
				>
					Hash P2P
				</button>
			</div>

			{/* Tab Content */}
			<div className="mt-6">
				{activeTab === 'transactions-verify' && renderTransactionsVerify()}
				{activeTab === 'transactions' && renderTransactions()}
				{activeTab === 'hash-group' && renderHashGroup()}
				{activeTab === 'hash-p2p' && renderHashP2P()}
			</div>
		</div>
	)
}
