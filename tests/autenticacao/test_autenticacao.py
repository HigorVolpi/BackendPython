import random
import string
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def random_username():
    return "testuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def test_registar_novo_usuario():
    nome_usuario = random_username()
    novo_usuario = {"nome_usuario": nome_usuario, "senha": "testpassword", "papel": "admin"}

    response = client.post("/auth/register", json=novo_usuario)

    assert response.status_code == 200
    assert response.json() == {"msg": "Usuário criado com sucesso"}

def test_registrar_usuario_repetido():
    nome_usuario = random_username()
    user_data = {"nome_usuario": nome_usuario, "senha": "testpassword", "papel": "admin"}

    # cria o usuário a primeira vez
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 200

    # tenta criar o mesmo usuário de novo, deve dar erro
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Usuário já existe"