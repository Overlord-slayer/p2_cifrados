// src/components/chat/MessageBubble.tsx
import React from 'react'
import { MessageResponse } from '../../types'
import { HiOutlinePencilAlt } from 'react-icons/hi'

interface Props {
  msg: MessageResponse
  me: boolean
}

export default function MessageBubble({ msg, me }: Props) {
  return (
    <div className={`mb-2 flex ${me ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`p-3 rounded-lg max-w-xs break-words ${
          me ? 'bg-blue-600 text-white' : 'bg-gray-700 text-white'
        }`}
      >
        {msg.message}
        <div className="mt-1 text-xs text-gray-300 flex items-center justify-end space-x-1">
          {msg.signature && <HiOutlinePencilAlt className="w-4 h-4" />}
          <span>
            {new Date(msg.timestamp).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </span>
        </div>
      </div>
    </div>
  )
}
