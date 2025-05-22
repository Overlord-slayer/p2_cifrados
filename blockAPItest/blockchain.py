from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import hashlib
import json
from datetime import datetime, timezone
import threading
import os

DATA_FILE = "cadenas.json"  # Archivo donde se almacenará la cadena de bloques

app = FastAPI()
chain_lock = threading.Lock()  # Lock para asegurar acceso seguro a la cadena en entornos concurrentes

class Transaction(BaseModel):
    nombre: str
    fecha_envio: str  
    data_enviada: Dict[str, Any]  

class Block(BaseModel):
    index: int
    timestamp: str  
    transaction: Transaction  
    previous_hash: str  
    hash: str  

class Blockchain:
    def __init__(self):
        # Inicializa la cadena: carga desde archivo si existe, si no, crea el bloque génesis
        self.chain: List[Block] = []
        if os.path.exists(DATA_FILE):
            self._load_chain()
        else:
            self.create_genesis_block()
            self._save_chain()

    def create_genesis_block(self):
        # Crea el primer bloque de la cadena con valores por defecto
        genesis_tx = Transaction(
            nombre="genesis",
            fecha_envio=datetime.now(timezone.utc).isoformat(),
            data_enviada={"message": "Genesis Block"}
        )
        genesis = Block(
            index=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            transaction=genesis_tx,
            previous_hash="0",
            hash=""
        )
        # Calcula y asigna el hash del bloque génesis
        genesis.hash = self.hash_block(genesis)
        self.chain.append(genesis)

    def get_last_block(self) -> Block:
        # Devuelve el último bloque de la cadena
        return self.chain[-1]

    def hash_block(self, block: Block) -> str:
        # Genera el hash SHA-256 basado en el contenido del bloque
        block_data = {
            "index": block.index,
            "timestamp": block.timestamp,
            "transaction": block.transaction.model_dump(),
            "previous_hash": block.previous_hash
        }
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, transaction: Transaction) -> Block:
        # Añade un nuevo bloque a la cadena usando la transacción proporcionada
        with chain_lock:
            last = self.get_last_block()
            new_block = Block(
                index=last.index + 1,
                timestamp=datetime.now(timezone.utc).isoformat(),
                transaction=transaction,
                previous_hash=last.hash,
                hash=""
            )
            new_block.hash = self.hash_block(new_block)
            self.chain.append(new_block)
            self._save_chain()  # Guarda la cadena actualizada en disco
            return new_block

    def is_chain_valid(self) -> bool:
        # Verifica la integridad de la cadena revisando hashes y referencias
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.previous_hash != prev.hash:
                return False  # El enlace con el bloque anterior no coincide
            if self.hash_block(curr) != curr.hash:
                return False  # El hash calculado no coincide con el almacenado
        return True

    def _save_chain(self):
        # Guarda la cadena de bloques completa en un archivo JSON
        with open(DATA_FILE, 'w') as f:
            json.dump([blk.model_dump() for blk in self.chain], f, indent=2)

    def _load_chain(self):
        # Carga la cadena de bloques desde un archivo JSON
        with open(DATA_FILE) as f:
            data = json.load(f)
            self.chain = [Block(**blk) for blk in data]

# Instancia global de la cadena de bloques
blockchain = Blockchain()

@app.post("/transactions", response_model=Block)
def create_transaction(tx: Transaction):
    # Endpoint para crear una nueva transacción y añadir un bloque
    return blockchain.add_block(tx)

@app.get("/transactions", response_model=List[Block])
def get_transactions():
    # Endpoint para obtener toda la cadena de bloques
    return blockchain.chain

@app.get("/block/{index}", response_model=Block)
def get_block(index: int):
    # Endpoint para obtener un bloque por su índice
    try:
        return blockchain.chain[index]
    except IndexError:
        # Si el índice no existe, lanza un error 404
        raise HTTPException(status_code=404, detail="Bloque no encontrado")

@app.get("/last_block", response_model=Block)
def last_block():
    # Endpoint para obtener el último bloque de la cadena
    return blockchain.get_last_block()

@app.get("/validate")
def validate_chain():
    # Endpoint para validar la integridad de la cadena
    return {"chain_valid": blockchain.is_chain_valid()}

if __name__ == "__main__":
    # Configuración para ejecutar la API con uvicorn
    import uvicorn
    uvicorn.run("blockchain:app", host="0.0.0.0", port=8000, reload=True)
    