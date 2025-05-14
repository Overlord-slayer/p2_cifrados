from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv
import os

# from app.model.models import User

# Cargar variables de entorno
load_dotenv()

# Obtener URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

def create_database_if_not_exists():
	# Parse the URL
	url = make_url(DATABASE_URL)
	target_db = url.database

	# Modify URL to connect to 'postgres' database instead
	url = url.set(database="postgres")

	# Create engine for the 'postgres' database
	engine = create_engine(url, isolation_level="AUTOCOMMIT")

	with engine.connect() as conn:
		# Check if the target database exists
		result = conn.execute(
			text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target_db}
		)
		exists = result.scalar() is not None

		if not exists:
			conn.execute(
				text(f'CREATE DATABASE "{target_db}"')
			)  # Double quotes preserve case sensitivity

	engine.dispose()

# Crear engine con manejo de excepciones
def create_engine_with_error_handling():
	try:
		return create_engine(
			DATABASE_URL,
			pool_size=10,
			max_overflow=20,
			pool_timeout=30,
			pool_recycle=3600,
		)
	except SQLAlchemyError as e:
		print(f"Error al conectar a la base de datos: {e}")
		raise

create_database_if_not_exists()

# Crear el engine y verificar la conexión
engine = create_engine_with_error_handling()

# Crear session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	totp_secret = Column(String, nullable=True)
	public_key = Column(
		LargeBinary, nullable=True
	)  # ECC/RSA pública para cifrado o firma
	is_active = Column(Boolean, default=True)

	# Nuevos campos
	is_google_account = Column(
		Boolean, default=False
	)  # Indica si el usuario usó Google
	email_verified = Column(
		Boolean, default=False
	)  # Por si quieres manejar verificación
	totp_verified = Column(Boolean, default=False)  # True después de escanear QR

class P2P_Message(Base):
	__tablename__ = "p2p_messages"

	id = Column(Integer, primary_key=True, index=True)
	
	sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	
	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	# Relationships to link to User
	sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
	receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")

class Group(Base):
	__tablename__ = "groups"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)

class GroupMembership(Base):
	__tablename__ = "group_memberships"

	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
	joined_at = Column(DateTime, default=datetime.utcnow)

	user = relationship("User", backref="group_memberships")
	group = relationship("Group", backref="memberships")

class GroupMessage(Base):
	__tablename__ = "group_messages"

	id = Column(Integer, primary_key=True, index=True)
	group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
	sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	message = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)

	group = relationship("Group", backref="messages")
	sender = relationship("User", backref="group_messages")

# Crear tablas si no existen
def create_tables():
	Base.metadata.create_all(bind=engine)

# Verificar conexión a la base de datos
def check_connection(engine):
	try:
		with engine.connect() as connection:
			connection.execute(text("SELECT 1"))  # <- Aquí el cambio
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