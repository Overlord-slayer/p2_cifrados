from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from typing import *

from app.auth.dependencies import get_current_user
from app.schemas.schemas import *

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.db import get_db
from app.model.models import *

load_dotenv()

class BlockchainManager:
	def __init__(self, db_session):
		self.db : Session = db_session

	def get_last_block(self):
		return self.db.query(Block).order_by(Block.id.desc()).first()

	def create_block(self, messages: List[BlockMessage]):
		last_block = self.get_last_block()
		previous_hash = last_block.hash if last_block else "0"

		# Simple hash based on message content
		message_data = []
		for message in messages:
			message_data.append(f"{message.is_p2p}:{message.message_id}:{message.message_hash}:{message.message_str}")

		block_string = json.dumps(message_data)
		block_hash = hashlib.sha256((block_string + previous_hash).encode()).hexdigest()

		new_block = Block(
			hash=block_hash,
			previous_hash=previous_hash,
			messages=messages,
			block_string=block_string
		)
		self.db.add(new_block)
		self.db.commit()
		return new_block

	def add_message(self, is_p2p, message_id):
		if is_p2p:
			db_message = self.db.query(P2P_Message).filter(P2P_Message.id == message_id).first()
		else:
			db_message = self.db.query(GroupMessage).filter(GroupMessage.id == message_id).first()

		new_msg = BlockMessage(
			is_p2p=is_p2p,
			message_id=message_id,
			message_str=json.loads(db_message.message)["mensaje"],
			message_hash=db_message.hash
		)
		self.db.add(new_msg)
		self.db.commit()

		# Check if a new block should be created
		unassigned = (
			self.db.query(BlockMessage)
			.filter(BlockMessage.block_id == None)
			.limit(4)
			.all()
		)

		if len(unassigned) == 4:
			self.create_block(unassigned)
			for m in unassigned:
				m.block_id = self.get_last_block().id
			self.db.commit()

	def get_all_blocks(self):
		blocks: List[Block] = (
			self.db.query(Block)
			.order_by(Block.id.asc())
			.all()
		)

		result = []
		for block in blocks:
			block_info = {
				"id": block.id,
				"hash": block.hash,
				"previous_hash": block.previous_hash,
				"timestamp": block.timestamp.isoformat(),
				"messages": [],
				"block_string": block.block_string
			}

			for msg in block.messages:
				block_info["messages"].append({
					"is_p2p": msg.is_p2p,
					"message_id": msg.message_id,
					"message": msg.message_str,
					"message_hash": msg.message_hash
				})

			result.append(block_info)

		return result

	def verify_blockchain(self):
		blocks: List[Block] = self.db.query(Block).order_by(Block.id.asc()).all()

		if not blocks:
			return True, "No blocks found. Blockchain is empty."

		for i, block in enumerate(blocks):
			# Recompute the hash from message contents and previous hash
			messages: List[BlockMessage] = sorted(block.messages, key=lambda m: m.id)  # consistent order
			
			message_data = []
			for message in messages:
				message_data.append(f"{message.is_p2p}:{message.message_id}:{message.message_hash}:{json.loads(message.message_str)['mensaje']}")

			previous_hash = blocks[i - 1].hash if i > 0 else "0"
			block_string = json.dumps(message_data)
			recalculated_hash = hashlib.sha256((block_string + previous_hash).encode() ).hexdigest()

			if block.hash != recalculated_hash:
				return False, f"Block {block.id} hash mismatch! Stored: {block.hash}, Recalculated: {recalculated_hash}"

			if i > 0 and block.previous_hash != blocks[i - 1].hash:
				return False, f"Block {block.id} previous_hash mismatch with Block {blocks[i - 1].id}"

		return True, f"Blockchain is valid. Calculated {len(blocks)} blocks."

router = APIRouter(prefix="", tags=["chat"])

@router.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
	manager = BlockchainManager(db)
	return manager.get_all_blocks()

@router.get("/verify-transactions")
def get_transactions(db: Session = Depends(get_db)):
	manager = BlockchainManager(db)
	return manager.verify_blockchain()