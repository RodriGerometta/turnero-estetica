from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, time

from database import get_db
from models import Admin, Empleada, Servicio, Turno
from auth import verify_password, create_session_token, get_current_admin

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


# ---------- LOGIN ----------

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin or not verify_password(password, admin.hashed_password):
        return templates.TemplateResponse(
            "admin_login.html", {"request": request, "error": "Usuario o contraseña incorrectos"}
        )
    token = create_session_token(admin.username)
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    response.set_cookie(key="session", value=token, httponly=True, max_age=60 * 60 * 8)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("session")
    return response


# ---------- DASHBOARD ----------

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    turnos = db.query(Turno).filter(Turno.fecha >= date.today()).order_by(Turno.fecha, Turno.hora_inicio).all()
    empleadas = db.query(Empleada).all()
    servicios = db.query(Servicio).all()
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "turnos": turnos,
            "empleadas": empleadas,
            "servicios": servicios,
            "admin_user": admin_user,
        },
    )


# ---------- EMPLEADAS ----------

@router.post("/empleadas")
def crear_empleada(
    nombre: str = Form(...),
    hora_inicio_jornada: time = Form(...),
    hora_fin_jornada: time = Form(...),
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    empleada = Empleada(nombre=nombre, hora_inicio_jornada=hora_inicio_jornada, hora_fin_jornada=hora_fin_jornada)
    db.add(empleada)
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/empleadas/{empleada_id}/toggle")
def toggle_empleada(empleada_id: int, db: Session = Depends(get_db), admin_user: str = Depends(get_current_admin)):
    empleada = db.query(Empleada).get(empleada_id)
    if not empleada:
        raise HTTPException(status_code=404)
    empleada.activo = not empleada.activo
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ---------- SERVICIOS ----------

@router.post("/servicios")
def crear_servicio(
    nombre: str = Form(...),
    duracion_min: int = Form(...),
    precio: float = Form(None),
    db: Session = Depends(get_db),
    admin_user: str = Depends(get_current_admin),
):
    servicio = Servicio(nombre=nombre, duracion_min=duracion_min, precio=precio)
    db.add(servicio)
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


@router.post("/servicios/{servicio_id}/toggle")
def toggle_servicio(servicio_id: int, db: Session = Depends(get_db), admin_user: str = Depends(get_current_admin)):
    servicio = db.query(Servicio).get(servicio_id)
    if not servicio:
        raise HTTPException(status_code=404)
    servicio.activo = not servicio.activo
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)


# ---------- TURNOS ----------

@router.post("/turnos/{turno_id}/cancelar")
def cancelar_turno(turno_id: int, db: Session = Depends(get_db), admin_user: str = Depends(get_current_admin)):
    turno = db.query(Turno).get(turno_id)
    if not turno:
        raise HTTPException(status_code=404)
    turno.estado = "cancelado"
    db.commit()
    return RedirectResponse(url="/admin/dashboard", status_code=303)
