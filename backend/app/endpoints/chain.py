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
		self.db = db_session

	def get_last_block(self):
		return self.db.query(Block).order_by(Block.id.desc()).first()

	def create_block(self, messages):
		last_block = self.get_last_block()
		previous_hash = last_block.hash if last_block else "0"

		# Simple hash based on message content
		message_data = [f"{m.message_type}:{m.message_id}" for m in messages]
		block_string = json.dumps(message_data) + previous_hash
		block_hash = hashlib.sha256(block_string.encode()).hexdigest()

		new_block = Block(
			hash=block_hash,
			previous_hash=previous_hash,
			messages=messages
		)
		self.db.add(new_block)
		self.db.commit()
		return new_block

	def add_message(self, message_type, message_id):
		new_msg = BlockMessage(message_type=message_type, message_id=message_id)
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
		blocks = (
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
				"messages": []
			}

			for msg in block.messages:
				block_info["messages"].append({
					"type": msg.message_type,
					"message_id": msg.message_id
				})

			result.append(block_info)

		return result

router = APIRouter(prefix="", tags=["chat"])

@router.get("/transactions")
def get_transactions(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
	manager = BlockchainManager(db)
	return manager.get_all_blocks()