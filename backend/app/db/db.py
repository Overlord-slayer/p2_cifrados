from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

# from app.model.models import User


# Cargar variables de entorno
load_dotenv()

# Obtener URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear engine con manejo de excepciones
def create_engine_with_error_handling():
    try:
        return create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=3600
        )
    except SQLAlchemyError as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise

# Crear el engine y verificar la conexión
engine = create_engine_with_error_handling()

# Crear session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Crear tablas si no existen
def create_tables():
    Base.metadata.create_all(bind=engine)

# Verificar conexión a la base de datos
def check_connection(engine):
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        print("Conexión a la base de datos exitosa.")
    except SQLAlchemyError as e:
        print(f"Error al conectar a la base de datos: {e}")

# Llamar a la función para crear tablas y verificar la conexión
create_tables()
check_connection(engine)

# Función para obtener la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # Deshacer cualquier cambio en caso de error
        raise e
    finally:
        db.close()

# def clear_cache(db, user_id):
#     # Obtener el usuario con la sesión actual
#     user = db.query(User).filter(User.id == user_id).first()
    
#     # Refrescar el objeto para obtener datos más actualizados
#     db.refresh(user)
    
#     # Alternativamente, puedes hacer commit y cerrar la sesión para liberar la caché
#     db.commit()
#     db.close()

#     return user
