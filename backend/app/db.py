from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL de conexión (puede venir de un .env)
DATABASE_URL = "postgresql://postgres:root@localhost:5432/chat_app"

# Crear el engine
engine = create_engine(DATABASE_URL)

# Crear session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()
