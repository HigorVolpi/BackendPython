from fastapi import FastAPI
from autenticacao.routers import autenticacao
from shared.database import engine, Base
from autenticacao.models.autenticacao import Tabela_Usuarios

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(autenticacao.router)
