from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import hashlib, json
from datetime import datetime, timezone
import databases
import sqlalchemy
from contextlib import asynccontextmanager
 
DATABASE_URL = "postgresql+asyncpg://postgre:admin@localhost:5432/ChatBlockchain"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

blockchain_table = sqlalchemy.Table(
    "blockchain",
    metadata,
    sqlalchemy.Column("index", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("timestamp", sqlalchemy.Text),
    sqlalchemy.Column("nombre", sqlalchemy.Text),
    sqlalchemy.Column("fecha_envio", sqlalchemy.Text),
    sqlalchemy.Column("data_enviada", sqlalchemy.JSON),
    sqlalchemy.Column("previous_hash", sqlalchemy.Text),
    sqlalchemy.Column("hash", sqlalchemy.Text),
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    query = "SELECT COUNT(*) FROM blockchain"
    count = await database.fetch_val(query=query)
    if count == 0:
        await create_genesis_block()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

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

def hash_block(block: Block) -> str:
    block_data = {
        "index": block.index,
        "timestamp": block.timestamp,
        "transaction": block.transaction.model_dump(),
        "previous_hash": block.previous_hash
    }
    block_string = json.dumps(block_data, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

async def get_last_block() -> Block:
    query = blockchain_table.select().order_by(blockchain_table.c.index.desc()).limit(1)
    result = await database.fetch_one(query)
    return db_row_to_block(result)

def db_row_to_block(row) -> Block:
    return Block(
        index=row["index"],
        timestamp=row["timestamp"],
        transaction=Transaction(
            nombre=row["nombre"],
            fecha_envio=row["fecha_envio"],
            data_enviada=row["data_enviada"]
        ),
        previous_hash=row["previous_hash"],
        hash=row["hash"]
    )

async def create_genesis_block():
    genesis_tx = Transaction(
        nombre="genesis",
        fecha_envio=datetime.now(timezone.utc).isoformat(),
        data_enviada={"message": "Genesis Block"}
    )
    genesis_block = Block(
        index=0,
        timestamp=datetime.now(timezone.utc).isoformat(),
        transaction=genesis_tx,
        previous_hash="0",
        hash=""
    )
    genesis_block.hash = hash_block(genesis_block)
    query = blockchain_table.insert().values(
        index=genesis_block.index,
        timestamp=genesis_block.timestamp,
        nombre=genesis_tx.nombre,
        fecha_envio=genesis_tx.fecha_envio,
        data_enviada=genesis_tx.data_enviada,
        previous_hash=genesis_block.previous_hash,
        hash=genesis_block.hash,
    )
    await database.execute(query)

@app.post("/transactions", response_model=Block)
async def create_transaction(tx: Transaction):
    last_block = await get_last_block()
    new_block = Block(
        index=last_block.index + 1,
        timestamp=datetime.now(timezone.utc).isoformat(),
        transaction=tx,
        previous_hash=last_block.hash,
        hash=""
    )
    new_block.hash = hash_block(new_block)
    query = blockchain_table.insert().values(
        index=new_block.index,
        timestamp=new_block.timestamp,
        nombre=tx.nombre,
        fecha_envio=tx.fecha_envio,
        data_enviada=tx.data_enviada,
        previous_hash=new_block.previous_hash,
        hash=new_block.hash,
    )
    await database.execute(query)
    return new_block

@app.get("/transactions", response_model=List[Block])
async def get_transactions():
    query = blockchain_table.select().order_by(blockchain_table.c.index)
    rows = await database.fetch_all(query)
    return [db_row_to_block(row) for row in rows]

@app.get("/block/{index}", response_model=Block)
async def get_block(index: int):
    query = blockchain_table.select().where(blockchain_table.c.index == index)
    row = await database.fetch_one(query)
    if row is None:
        raise HTTPException(status_code=404, detail="Bloque no encontrado")
    return db_row_to_block(row)

@app.get("/last_block", response_model=Block)
async def last_block():
    return await get_last_block()

@app.get("/validate")
async def validate_chain():
    query = blockchain_table.select().order_by(blockchain_table.c.index)
    rows = await database.fetch_all(query)
    for i in range(1, len(rows)):
        prev = db_row_to_block(rows[i - 1])
        curr = db_row_to_block(rows[i])
        if curr.previous_hash != prev.hash or hash_block(curr) != curr.hash:
            return {"chain_valid": False}
    return {"chain_valid": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("blockchain:app", host="0.0.0.0", port=8000, reload=True)
