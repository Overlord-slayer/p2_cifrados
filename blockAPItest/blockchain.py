from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any, Dict
import hashlib
import time
import json

app = FastAPI()

class Transaction(BaseModel):
    nombre: str
    fecha_envio: str  
    data_enviada: Dict[str, Any]

class Block(BaseModel):
    index: int
    timestamp: float
    transaction: Transaction
    previous_hash: str
    hash: str

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()

    def create_genesis_block(self) -> Block:
        genesis_transaction = Transaction(
            nombre="genesis",
            fecha_envio=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            data_enviada={"message": "Genesis Block"}
        )
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transaction=genesis_transaction,
            previous_hash="0",
            hash="0"
        )
        self.chain.append(genesis_block)
        return genesis_block

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def hash_block(self, block: Block) -> str:
        # Prepare block data string
        block_string = json.dumps({
            "index": block.index,
            "timestamp": block.timestamp,
            "transaction": block.transaction.dict(),
            "previous_hash": block.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, transaction: Transaction) -> Block:
        last_block = self.get_last_block()
        index = last_block.index + 1
        timestamp = time.time()
        previous_hash = last_block.hash
        new_block = Block(
            index=index,
            timestamp=timestamp,
            transaction=transaction,
            previous_hash=previous_hash,
            hash=""
        )
        new_block.hash = self.hash_block(new_block)
        self.chain.append(new_block)
        return new_block

# Instantiate the blockchain
blockchain = Blockchain()

@app.post("/transactions", response_model=Block)
def create_transaction(transaction: Transaction):
    """
    Guarda una nueva transacción en el blockchain.
    """
    new_block = blockchain.add_block(transaction)
    return new_block

@app.get("/transactions", response_model=List[Block])
def get_transactions():
    """
    Obtiene todo el historial de bloques (blockchain completo).
    """
    return blockchain.chain
