from pydantic import BaseModel
from datetime import date, time
from typing import Optional


class EmpleadaBase(BaseModel):
    nombre: str
    activo: bool = True
    hora_inicio_jornada: time
    hora_fin_jornada: time


class EmpleadaCreate(EmpleadaBase):
    pass


class EmpleadaOut(EmpleadaBase):
    id: int

    class Config:
        from_attributes = True


class ServicioBase(BaseModel):
    nombre: str
    duracion_min: int
    precio: Optional[float] = None
    activo: bool = True


class ServicioCreate(ServicioBase):
    pass


class ServicioOut(ServicioBase):
    id: int

    class Config:
        from_attributes = True


class TurnoCreate(BaseModel):
    empleada_id: int
    servicio_id: int
    cliente_nombre: str
    cliente_telefono: str
    fecha: date
    hora_inicio: time


class TurnoOut(BaseModel):
    id: int
    empleada_id: int
    servicio_id: int
    cliente_nombre: str
    cliente_telefono: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: str

    class Config:
        from_attributes = True
