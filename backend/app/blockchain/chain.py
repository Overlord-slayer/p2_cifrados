import hashlib
import time
import json

def hash_block(block):
	block_string = json.dumps(
		block, sort_keys=True
	).encode()  # Convert block to string and encode it
	return hashlib.sha256(
		block_string
	).hexdigest()  # Return the SHA-256 hash of the block

def create_block(previous_hash, data):
	return {
		"index": 0,
		"timestamp": time.time(),
		"data": data,
		"previous_hash": previous_hash,
		"hash": "",
	}

def create_genesis_block():
	return create_block("0", "Genesis Block")

def add_block(previous_block, data):
	block = create_block(previous_block["hash"], data)
	block["index"] = previous_block["index"] + 1
	block["hash"] = hash_block(block)
	return block

class Blockchain:
	def __init__(self):
		self.chain = [create_genesis_block()]
		self.current_transactions = []

	def last_block(self):
		return self.chain[-1]

	def add_transaction(self, transaction):
		self.current_transactions.append(transaction)

	def mine_block(self):
		last_block = self.last_block()
		new_block = add_block(last_block, self.current_transactions)
		self.chain.append(new_block)
		self.current_transactions = []  # Reset transactions for the next block
		return new_block