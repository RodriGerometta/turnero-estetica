from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Empleada(Base):
    __tablename__ = "empleadas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
    hora_inicio_jornada = Column(Time, nullable=False)  # ej: 09:00
    hora_fin_jornada = Column(Time, nullable=False)     # ej: 19:00

    turnos = relationship("Turno", back_populates="empleada")


class Servicio(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    duracion_min = Column(Integer, nullable=False)  # duración en minutos
    precio = Column(Float, nullable=True)
    activo = Column(Boolean, default=True)

    turnos = relationship("Turno", back_populates="servicio")


class Turno(Base):
    __tablename__ = "turnos"

    id = Column(Integer, primary_key=True, index=True)
    empleada_id = Column(Integer, ForeignKey("empleadas.id"), nullable=False)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)

    cliente_nombre = Column(String, nullable=False)
    cliente_telefono = Column(String, nullable=False)

    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    estado = Column(String, default="confirmado")  # confirmado / cancelado

    empleada = relationship("Empleada", back_populates="turnos")
    servicio = relationship("Servicio", back_populates="turnos")
