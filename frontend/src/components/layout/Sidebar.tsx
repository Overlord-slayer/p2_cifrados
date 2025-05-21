// src/components/layout/Sidebar.tsx

import React from 'react'

interface Props {
  contacts: { email: string }[]
  active: string
  onSelect: (email: string) => void
}

export default function Sidebar({ contacts, active, onSelect }: Props) {
  return (
    <aside className="w-1/4 bg-gray-800 text-white p-4">
      <h2 className="mb-4 text-xl font-semibold">Contacts</h2>
      {contacts.map(c => (
        <div
          key={c.email}
          onClick={() => onSelect(c.email)}
          className={`cursor-pointer p-2 rounded ${
            active === c.email ? 'bg-gray-700' : 'hover:bg-gray-700'
          }`}
        >
          {c.email}
        </div>
      ))}
    </aside>
  )
}
