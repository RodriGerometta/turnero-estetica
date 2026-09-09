from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from routers import public, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Turnero Estética")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(public.router)
app.include_router(admin.router)
