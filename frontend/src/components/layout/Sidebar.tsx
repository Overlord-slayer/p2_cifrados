import React from 'react'
import { HiUsers, HiOutlineUser, HiOutlineUsers } from 'react-icons/hi'
import './Sidebar.css'

interface Props {
  contacts: { email: string }[]
  active: string
  onSelect: (email: string) => void
}

export default function Sidebar({ contacts, active, onSelect }: Props) {
  // Ponemos 'Group Chat' al principio de la lista
  const items = [{ email: 'Group Chat' }, ...contacts]

  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">
        <HiUsers className="sidebar-icon" />
        Contacts
      </h2>
      <div className="contact-list">
        {items.map(c => {
          const isActive = c.email === active
          const Icon = c.email === 'Group Chat' ? HiOutlineUsers : HiOutlineUser

          return (
            <div
              key={c.email}
              className={`contact-item ${isActive ? 'active' : ''}`}
              onClick={() => onSelect(c.email)}
            >
              <Icon className="contact-icon" />
              <span className="contact-label">{c.email}</span>
            </div>
          )
        })}
      </div>
    </aside>
  )
}

