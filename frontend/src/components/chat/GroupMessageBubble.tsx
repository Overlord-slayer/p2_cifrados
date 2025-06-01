// src/components/chat/MessageBubble.tsx
import React from 'react'
import { MessageResponse } from '../../types'
import { HiOutlinePencilAlt } from 'react-icons/hi'
import './MessageBubble.css'

interface Props {
	msg: MessageResponse
	me: boolean
}

export default function GroupMessageBubble({ msg, me }: Props) {
	return (
		<div className={`bubble-wrapper ${me ? 'right' : 'left'}`}>
			<div className={`bubble ${me ? 'bubble-me' : 'bubble-other'} ${msg.signature ? (msg.signature == "Signed" ? 'bubble-signed' : 'bubble-signed-error') : ''} `}>
				{!me && (
					<h4 style={{marginBottom: 10, fontWeight: 900 }}>
						{msg.sender}
					</h4>
				)}
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