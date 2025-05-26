from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_registar_novo_usuario():
    novo_usuario = {"nome_usuario": "testuser", "senha": "testpassword", "papel": "admin"}

    response = client.post("/auth/register", json=novo_usuario)

    assert response.status_code == 200
    assert response.json() == {"msg": "Usuário criado com sucesso"}

def test_registrar_usuario_repetido():
    client.post("/auth/register", json={"nome_usuario": "testuser", "senha": "testpassword", "papel": "admin"})
    response = client.post("/auth/register", json={"nome_usuario": "testuser", "senha": "testpassword", "papel": "admin"})
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Usuário já existe"