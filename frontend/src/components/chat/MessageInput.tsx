// src/components/chat/MessageInput.tsx

import React, { useState } from 'react'
import { HiOutlinePaperAirplane } from 'react-icons/hi'

interface Props {
  onSend: (text: string) => void
}

const MessageInput: React.FC<Props> = ({ onSend }) => {
  const [text, setText] = useState('')

  const handleSend = () => {
    if (!text.trim()) return
    onSend(text.trim())
    setText('')
  }

  return (
    <div className="flex items-center p-4 bg-gray-900">
      <input
        type="text"
        placeholder="Type a message..."
        value={text}
        onChange={e => setText(e.target.value)}
        className="flex-1 p-2 mr-2 bg-gray-800 text-white rounded"
      />
      <button
        onClick={handleSend}
        className="p-2 bg-blue-600 rounded hover:bg-blue-700"
      >
        <HiOutlinePaperAirplane className="w-5 h-5 text-white" />
      </button>
    </div>
  )
}

// 🔸 Export por defecto para que `import MessageInput from '…'` funcione
export default MessageInput
