// src/components/chat/SignToggle.tsx

import React from 'react'
import { HiOutlinePencilAlt } from 'react-icons/hi'
import './SignToggle.css'

interface Props {
  enabled: boolean
  onToggle: (value: boolean) => void
}

export default function SignToggle({ enabled, onToggle }: Props) {
  return (
    <div className="toggle-container">
      <input
        id="sign-toggle"
        type="checkbox"
        checked={enabled}
        onChange={e => onToggle(e.target.checked)}
        className="toggle-checkbox"
      />
      <label htmlFor="sign-toggle" className="toggle-label">
        <HiOutlinePencilAlt className="toggle-icon" />
        Sign Message
      </label>
    </div>
  )
}
