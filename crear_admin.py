"""
Script para crear el usuario admin la primera vez.
Correr: python crear_admin.py
"""
from database import Base, engine, SessionLocal
from models import Admin
from auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

username = input("Nombre de usuario para el admin: ")
password = input("Contraseña: ")

existente = db.query(Admin).filter(Admin.username == username).first()
if existente:
    print("Ese usuario ya existe.")
else:
    admin = Admin(username=username, hashed_password=hash_password(password))
    db.add(admin)
    db.commit()
    print(f"Admin '{username}' creado correctamente.")

db.close()
