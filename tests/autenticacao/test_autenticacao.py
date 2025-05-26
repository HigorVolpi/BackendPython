import random
import string
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def random_username():
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

@pytest.fixture
def novo_usuario():
    nome_usuario = random_username()
    return {"nome_usuario": nome_usuario, "senha": "testpassword", "papel": "admin"}

@pytest.fixture
def token(novo_usuario):
    # registra usuário
    client.post("/auth/register", json=novo_usuario)
    # login para pegar token
    response = client.post(
        "/auth/login",
        data={"username": novo_usuario["nome_usuario"], "password": novo_usuario["senha"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_registrar_novo_usuario(novo_usuario):
    response = client.post("/auth/register", json=novo_usuario)
    assert response.status_code == 201
    assert response.json() == {"msg": "Usuário criado com sucesso"}

def test_registrar_usuario_repetido(novo_usuario):
    client.post("/auth/register", json=novo_usuario)  # 1º vez
    response = client.post("/auth/register", json=novo_usuario)  # 2º vez, deve falhar
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário já existe"

def test_login_com_sucesso(novo_usuario):
    client.post("/auth/register", json=novo_usuario)
    response = client.post(
        "/auth/login",
        data={"username": novo_usuario["nome_usuario"], "password": novo_usuario["senha"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_com_credenciais_invalidas():
    response = client.post(
        "/auth/login",
        data={"username": "usuario_qualquer", "password": "senha_errada"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha incorretos"

def test_refresh_token(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/refresh-token", headers=headers)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"
