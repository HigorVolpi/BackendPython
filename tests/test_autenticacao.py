import pytest
from fastapi.testclient import TestClient
from autenticacao.routers.autenticacao import app

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_and_login():
    # Registra usuário
    response = client.post("/auth/register", json={"username": "teste", "password": "1234", "role": "user"})
    assert response.status_code == 200

    # Loga usuário
    response = client.post("/auth/login", data={"username": "teste", "password": "1234"})
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"


def test_admin_access():
    # Registro admin
    response = client.post("/auth/register", json={
        "username": "admin",
        "password": "adminpass",
        "role": "admin"
    })
    assert response.status_code == 200

    # Login admin
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "adminpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Admin pode deletar
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/produtos", headers=headers)
    assert response.status_code == 200
    assert "Produto deletado" in response.json()["msg"]

def test_user_cannot_delete():
    # Registro user
    response = client.post("/auth/register", json={
        "username": "normaluser",
        "password": "userpass",
        "role": "user"
    })
    assert response.status_code == 200

    # Login user
    response = client.post("/auth/login", data={
        "username": "normaluser",
        "password": "userpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    # User NÃO pode deletar
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/produtos", headers=headers)
    assert response.status_code == 403
