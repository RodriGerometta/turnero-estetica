# Turnero Estética

Sistema de reserva de turnos online: página pública para que los clientes saquen turno, y panel de administración para gestionar profesionales, servicios y turnos.

## Stack
- **Backend:** FastAPI (Python)
- **Base de datos:** SQLite (archivo `turnero.db`, se crea solo)
- **Frontend:** HTML + Jinja2 + HTMX (sin necesidad de escribir JS)

## Instalación

```bash
# 1. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear el usuario administrador (una sola vez)
python crear_admin.py
# Te va a pedir usuario y contraseña

# 4. Levantar el servidor
uvicorn main:app --reload
```

La app queda disponible en `http://127.0.0.1:8000`

- **Página pública de reserva:** `http://127.0.0.1:8000/`
- **Panel admin:** `http://127.0.0.1:8000/admin/login`

## Primeros pasos como admin

1. Entrá a `/admin/login` con el usuario que creaste.
2. Cargá al menos una **profesional** (nombre + horario de jornada, ej. 09:00 a 18:00).
3. Cargá al menos un **servicio** (nombre, duración en minutos, precio opcional).
4. Listo — ya en `/` los clientes pueden elegir servicio, profesional, fecha y ver los horarios libres.

## Cómo funciona la disponibilidad

El sistema calcula los horarios libres automáticamente:
- Toma la jornada laboral de la profesional elegida.
- Resta los turnos ya confirmados ese día.
- Considera la duración del servicio (un servicio de 60 min no va a ofrecer un slot que choque con el siguiente turno).
- Revalida todo en el momento de confirmar, para evitar que dos personas reserven el mismo horario al mismo tiempo.

## Estructura del proyecto

```
turnero/
├── main.py                 # App principal
├── database.py             # Configuración de la base de datos
├── models.py                # Tablas (Empleada, Servicio, Turno, Admin)
├── schemas.py                # Validaciones de datos
├── auth.py                    # Login del panel admin (sesión por cookie)
├── crear_admin.py            # Script para crear el usuario admin
├── routers/
│   ├── public.py              # Reserva de turnos (lado cliente)
│   └── admin.py                # Panel de administración
├── templates/                  # Vistas HTML
└── static/style.css            # Estilos
```

## Para producción (antes de entregarlo en vivo)

Estas son las cosas que hoy están simplificadas a propósito para MVP y que conviene ajustar antes de un uso real:

1. **`SECRET_KEY` en `auth.py`**: hoy es un valor fijo en el código. Cambiarla por una variable de entorno (`os.environ["SECRET_KEY"]`) antes de subir a producción.
2. **Base de datos**: SQLite alcanza para un solo local con tráfico bajo/medio. Si crece, migrar a PostgreSQL (con SQLAlchemy es solo cambiar la URL de conexión).
3. **Notificaciones**: no envía WhatsApp/mail al confirmar. Se puede sumar con Twilio (WhatsApp) o SMTP (mail) — avisame si lo necesitás y lo agrego.
4. **Deploy**: falta decidir dónde se aloja (Railway, Render, VPS propio, etc.). Cualquiera de esas corre esto sin cambios grandes.
5. **Backups**: si usan SQLite, conviene programar un backup periódico del archivo `turnero.db`.

## Notas

- Los turnos cancelados no se borran, quedan marcados como "cancelado" para mantener el historial.
- Una profesional o servicio "desactivado" deja de aparecer en la reserva pública, pero no se borra su historial.
