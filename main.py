from fastapi import FastAPI
from shared.database import engine, Base

# Configurações do FastAPI
from autenticacao.routers import autenticacao
from clientes.routers import clientes
from produtos.routers import produtos
from pedidos.routers import pedidos

# Configurações do banco de dados
from autenticacao.models.autenticacao import Tabela_Usuarios
from clientes.models.clientes import Cliente
from produtos.models.produtos import Produto
from pedidos.models.pedidos import Pedido

app = FastAPI()

app.include_router(autenticacao.router)
app.include_router(clientes.router, prefix="/clients", tags=["Clientes"])
app.include_router(produtos.router)
app.include_router(pedidos.router)