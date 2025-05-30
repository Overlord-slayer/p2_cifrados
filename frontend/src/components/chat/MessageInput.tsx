// src/components/chat/MessageInput.tsx

import React, { useState } from 'react'
import { HiOutlinePaperAirplane } from 'react-icons/hi'
import './MessageInput.css'

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
		<div className="input-container">
			<input
				type="text"
				placeholder="Type a message..."
				value={text}
				className="input-field"
				onChange={e => setText(e.target.value)}
				onKeyDown={(e) => {
					if (e.key === 'Enter') {
						handleSend();
					}
				}}
			/>
			<button onClick={handleSend} className="send-button">
				<HiOutlinePaperAirplane className="send-icon" />
			</button>
		</div>
	)
}

export default MessageInput
