import React from 'react'
import { HiUsers, HiOutlineUser, HiOutlineUsers } from 'react-icons/hi'
import './Sidebar.css'

interface Props {
  contacts: { id: string }[]
  active: string
  onSelect: (id: string) => void
}

export default function Sidebar({ contacts, active, onSelect }: Props) {
  // Ponemos 'Group Chat' al principio de la lista
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
          const Icon = c.id === 'Group Chat' ? HiOutlineUsers : HiOutlineUser

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

