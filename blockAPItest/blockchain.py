from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import hashlib
import json
from datetime import datetime
import threading
import os

DATA_FILE = "cadenas.json"

app = FastAPI()
chain_lock = threading.Lock()

class Transaction(BaseModel):
    nombre: str
    fecha_envio: str  # ISO 8601
    data_enviada: Dict[str, Any]

class Block(BaseModel):
    index: int
    timestamp: str  # ISO 8601
    transaction: Transaction
    previous_hash: str
    hash: str

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        if os.path.exists(DATA_FILE):
            self._load_chain()
        else:
            self.create_genesis_block()
            self._save_chain()

    def create_genesis_block(self):
        genesis_tx = Transaction(
            nombre="genesis",
            fecha_envio=datetime.utcnow().isoformat() + "Z",
            data_enviada={"message": "Genesis Block"}
        )
        genesis = Block(
            index=0,
            timestamp=datetime.utcnow().isoformat() + "Z",
            transaction=genesis_tx,
            previous_hash="0",
            hash=""
        )
        genesis.hash = self.hash_block(genesis)
        self.chain.append(genesis)

    def get_last_block(self) -> Block:
        return self.chain[-1]

    def hash_block(self, block: Block) -> str:
        block_data = {
            "index": block.index,
            "timestamp": block.timestamp,
            "transaction": block.transaction.dict(),
            "previous_hash": block.previous_hash
        }
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, transaction: Transaction) -> Block:
        with chain_lock:
            last = self.get_last_block()
            new_block = Block(
                index=last.index + 1,
                timestamp=datetime.utcnow().isoformat() + "Z",
                transaction=transaction,
                previous_hash=last.hash,
                hash=""
            )
            new_block.hash = self.hash_block(new_block)
            self.chain.append(new_block)
            self._save_chain()
            return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.previous_hash != prev.hash:
                return False
            if self.hash_block(curr) != curr.hash:
                return False
        return True

    def _save_chain(self):
        with open(DATA_FILE, 'w') as f:
            json.dump([blk.dict() for blk in self.chain], f, indent=2)

    def _load_chain(self):
        with open(DATA_FILE) as f:
            data = json.load(f)
            self.chain = [Block(**blk) for blk in data]

blockchain = Blockchain()

@app.post("/transactions", response_model=Block)
def create_transaction(tx: Transaction):
    return blockchain.add_block(tx)

@app.get("/transactions", response_model=List[Block])
def get_transactions():
    return blockchain.chain

@app.get("/block/{index}", response_model=Block)
def get_block(index: int):
    try:
        return blockchain.chain[index]
    except IndexError:
        raise HTTPException(status_code=404, detail="Bloque no encontrado")

@app.get("/last_block", response_model=Block)
def last_block():
    return blockchain.get_last_block()

@app.get("/validate")
def validate_chain():
    return {"chain_valid": blockchain.is_chain_valid()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("blockchain_chat:app", host="0.0.0.0", port=8000, reload=True)
