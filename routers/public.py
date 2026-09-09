from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta

from database import get_db
from models import Empleada, Servicio, Turno

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def calcular_horarios_disponibles(db: Session, empleada: Empleada, servicio: Servicio, fecha: date):
    """Devuelve una lista de horas (time) disponibles para ese día, según
    la jornada de la empleada, la duración del servicio y los turnos ya tomados."""
    duracion = timedelta(minutes=servicio.duracion_min)
    inicio_jornada = datetime.combine(fecha, empleada.hora_inicio_jornada)
    fin_jornada = datetime.combine(fecha, empleada.hora_fin_jornada)

    turnos_del_dia = (
        db.query(Turno)
        .filter(
            Turno.empleada_id == empleada.id,
            Turno.fecha == fecha,
            Turno.estado == "confirmado",
        )
        .all()
    )

    ocupados = [
        (datetime.combine(fecha, t.hora_inicio), datetime.combine(fecha, t.hora_fin))
        for t in turnos_del_dia
    ]

    slots = []
    cursor = inicio_jornada
    paso = timedelta(minutes=15)  # granularidad de los slots ofrecidos

    while cursor + duracion <= fin_jornada:
        fin_slot = cursor + duracion
        solapa = any(cursor < fin_o and fin_slot > inicio_o for inicio_o, fin_o in ocupados)
        if not solapa and cursor > datetime.now():
            slots.append(cursor.time())
        cursor += paso

    return slots


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    servicios = db.query(Servicio).filter(Servicio.activo == True).all()
    empleadas = db.query(Empleada).filter(Empleada.activo == True).all()
    return templates.TemplateResponse(
        "booking.html",
        {"request": request, "servicios": servicios, "empleadas": empleadas, "hoy": date.today()},
    )


@router.get("/horarios-disponibles", response_class=HTMLResponse)
def horarios_disponibles(
    request: Request,
    empleada_id: int,
    servicio_id: int,
    fecha: date,
    db: Session = Depends(get_db),
):
    empleada = db.query(Empleada).get(empleada_id)
    servicio = db.query(Servicio).get(servicio_id)
    if not empleada or not servicio:
        raise HTTPException(status_code=404, detail="Empleada o servicio no encontrado")

    slots = calcular_horarios_disponibles(db, empleada, servicio, fecha)

    return templates.TemplateResponse(
        "_horarios_partial.html",
        {
            "request": request,
            "slots": slots,
            "empleada_id": empleada_id,
            "servicio_id": servicio_id,
            "fecha": fecha,
        },
    )


@router.post("/reservar", response_class=HTMLResponse)
def reservar(
    request: Request,
    empleada_id: int = Form(...),
    servicio_id: int = Form(...),
    fecha: date = Form(...),
    hora_inicio: time = Form(...),
    cliente_nombre: str = Form(...),
    cliente_telefono: str = Form(...),
    db: Session = Depends(get_db),
):
    empleada = db.query(Empleada).get(empleada_id)
    servicio = db.query(Servicio).get(servicio_id)
    if not empleada or not servicio:
        raise HTTPException(status_code=404, detail="Empleada o servicio no encontrado")

    # Revalidar disponibilidad server-side antes de confirmar (evita choques de turnos)
    slots_disponibles = calcular_horarios_disponibles(db, empleada, servicio, fecha)
    if hora_inicio not in slots_disponibles:
        return templates.TemplateResponse(
            "_error_partial.html",
            {"request": request, "mensaje": "Ese horario ya no está disponible. Elegí otro."},
        )

    inicio_dt = datetime.combine(fecha, hora_inicio)
    fin_dt = inicio_dt + timedelta(minutes=servicio.duracion_min)

    nuevo_turno = Turno(
        empleada_id=empleada_id,
        servicio_id=servicio_id,
        cliente_nombre=cliente_nombre,
        cliente_telefono=cliente_telefono,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=fin_dt.time(),
        estado="confirmado",
    )
    db.add(nuevo_turno)
    db.commit()
    db.refresh(nuevo_turno)

    return templates.TemplateResponse(
        "_confirmacion_partial.html",
        {"request": request, "turno": nuevo_turno, "empleada": empleada, "servicio": servicio},
    )
