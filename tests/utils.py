import random
import string
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def random_string(prefix="", size=6):
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))

def criar_token_admin():
    admin_credentials = {"nome_usuario": "admin", "senha": "admin123"}
    response = client.post("/auth/login", data=admin_credentials)
    assert response.status_code == 200
    return response.json()["access_token"]

def criar_cliente_com_dados(token=None):
    nome = random_string("Cliente_")
    email = f"{nome}@exemplo.com"
    cpf = ''.join(random.choices(string.digits, k=11))

    cliente_data = {
        "nome": nome,
        "email": email,
        "cpf": cpf
    }

    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/clients/", json=cliente_data, headers=headers)
    assert response.status_code == 201
    return response.json()

def criar_produto_simples(token=None):
    nome = random_string("Produto_")
    codigo_barras = ''.join(random.choices(string.digits, k=13))
    produto_data = {
        "nome": nome,
        "codigo_barras": codigo_barras,
        "valor_venda": 10.0,
        "estoque_inicial": 100,
        "secao": "geral",
        "disponivel": True
    }

    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/products/", json=produto_data, headers=headers)
    assert response.status_code == 201
    return response.json()
