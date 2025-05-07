from time import time
import hashlib
import json

class Blockchain:
	def __init__(self):
		self.chain = []
		self.current_transactions = []
		self.new_block(previous_hash="1", proof=100)

	def new_block(self, proof, previous_hash=None):
		block = {
			"index": len(self.chain) + 1,
			"timestamp": time(),
			"transactions": self.current_transactions,
			"proof": proof,
			"previous_hash": previous_hash or self.hash(self.chain[-1]),
		}
		self.current_transactions = []
		self.chain.append(block)
		return block

	def add_transaction(self, sender: str, receiver: str, message: bytes):
		self.current_transactions.append(
			{
				"sender": sender,
				"receiver": receiver,
				"message": message,
			}
		)

		# Automatically create a new block when 16 transactions are added
		if len(self.current_transactions) >= 16:
			self.new_block(proof=self.proof_of_work(self.last_block))

		return self.last_block["index"] + 1

	def get_all_transactions(self):
		transactions = []
		for block in self.chain:
			transactions.extend(block["transactions"])
		transactions.extend(self.current_transactions)
		return transactions

	def proof_of_work(self, last_block):
		last_proof = last_block["proof"]
		proof = 0
		while not self.valid_proof(last_proof, proof):
			proof += 1
		return proof

	def valid_proof(last_proof, proof):
		guess = f"{last_proof}{proof}".encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"

	def hash_block(block):
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

	def last_block(self):
		return self.chain[-1]