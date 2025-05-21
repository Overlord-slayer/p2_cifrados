// src/components/chat/SignToggle.tsx
import React from 'react'
import { HiOutlinePencilAlt } from 'react-icons/hi'

interface Props {
  enabled: boolean
  onToggle: (value: boolean) => void
}

export default function SignToggle({ enabled, onToggle }: Props) {
  return (
    <div className="flex items-center p-4 bg-gray-900 text-white">
      <input
        id="sign-toggle"
        type="checkbox"
        checked={enabled}
        onChange={e => onToggle(e.target.checked)}
        className="mr-2"
      />
      <label htmlFor="sign-toggle" className="flex items-center cursor-pointer">
        <HiOutlinePencilAlt className="w-5 h-5 mr-1" />
        Sign Message
      </label>
    </div>
  )
}
