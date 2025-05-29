import React from 'react'
import { HiUsers, HiOutlineUser } from 'react-icons/hi'
import './Sidebar.css'

interface Props {
	contacts: { id: string }[],
	username: string
	active: string
	onSelect: (id: string) => void
}

export default function Sidebar({ contacts, username, active, onSelect }: Props) {
	const items = [...contacts]

	return (
		<aside className="sidebar">
			<h2 className="sidebar-title">
				<HiUsers className="sidebar-icon" />
				Contacts
			</h2>
			<div className="contact-list">
				{items.map(c => {
					const isActive = c.id === active
					const Icon = HiOutlineUser
					if (c.id == username) return
					return (
						<div
							key={c.id}
							className={`contact-item ${isActive ? 'active' : ''}`}
							onClick={() => onSelect(c.id)}
						>
							<Icon className="contact-icon" />
							<span className="contact-label">{c.id}</span>
						</div>
					)
				})}
			</div>
		</aside>
	)
}