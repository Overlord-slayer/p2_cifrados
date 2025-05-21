// src/components/layout/Sidebar.tsx

import React from 'react'
import './Sidebar.css'

interface Props {
  contacts: { email: string }[]
  active: string
  onSelect: (email: string) => void
}

export default function Sidebar({ contacts, active, onSelect }: Props) {
  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">Contacts</h2>
      {contacts.map(c => (
        <div
          key={c.email}
          onClick={() => onSelect(c.email)}
          className={`sidebar-contact ${active === c.email ? 'active' : ''}`}
        >
          {c.email}
        </div>
      ))}
    </aside>
  )
}
