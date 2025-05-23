# init_db.py
from app.db.db import Base, engine
from app.model.models import User, P2P_Message, Group, GroupUser, GroupMessage

print("⏳ Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas correctamente.")
