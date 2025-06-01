// src/components/chat/MessageBubble.tsx
import React from 'react'
import { MessageResponse } from '../../types'
import { HiOutlinePencilAlt } from 'react-icons/hi'
import './MessageBubble.css'

interface Props {
	msg: MessageResponse
	me: boolean
}

export default function MessageBubble({ msg, me }: Props) {
	return (
		<div className={`bubble-wrapper ${me ? 'right' : 'left'}`}>
			<div className={`bubble ${me ? 'bubble-me' : 'bubble-other'} ${msg.signature ? 'bubble-signed' : ''}`}>
				{msg.message}
				<div className="bubble-meta">
					{msg.signature && <HiOutlinePencilAlt className="bubble-icon" />}
					<span className="bubble-time">
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