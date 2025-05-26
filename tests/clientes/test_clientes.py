import random
import string
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def gerar_nome_unico():
    return "Cliente Teste " + ''.join(random.choices(string.ascii_letters, k=5))

def gerar_email_unico():
    return ''.join(random.choices(string.ascii_lowercase, k=6)) + "@email.com"

def gerar_cpf():
    return ''.join(random.choices(string.digits, k=11))

def obter_token_admin():
    nome_usuario = "admin_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    senha = "adminpassword"
    usuario_data = {"nome_usuario": nome_usuario, "senha": senha, "papel": "admin"}
    client.post("/auth/register", json=usuario_data)
    response = client.post("/auth/login", data={"username": nome_usuario, "password": senha})
    return response.json()["access_token"]

def test_criar_novo_cliente():
    token = obter_token_admin()
    headers = {"Authorization": f"Bearer {token}"}
    
    cliente_data = {
        "nome": gerar_nome_unico(),
        "email": gerar_email_unico(),
        "cpf": gerar_cpf()
    }
    
    response = client.post("/clients/", json=cliente_data, headers=headers)
    assert response.status_code == 201 or response.status_code == 200
    assert "id" in response.json()

def test_criar_cliente_com_cpf_duplicado():
    token = obter_token_admin()
    headers = {"Authorization": f"Bearer {token}"}
    
    cpf = gerar_cpf()
    cliente_data = {
        "nome": gerar_nome_unico(),
        "email": gerar_email_unico(),
        "cpf": cpf
    }
    # Cria o cliente uma vez
    response1 = client.post("/clients/", json=cliente_data, headers=headers)
    assert response1.status_code == 201 or response1.status_code == 200

    # Tenta criar outro com o mesmo CPF
    cliente_data["email"] = gerar_email_unico()  # email diferente
    response2 = client.post("/clients/", json=cliente_data, headers=headers)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "CPF já cadastrado"

def test_listar_clients():
    token = obter_token_admin()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/clients/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_buscar_cliente_por_id():
    token = obter_token_admin()
    headers = {"Authorization": f"Bearer {token}"}
    
    cliente_data = {
        "nome": gerar_nome_unico(),
        "email": gerar_email_unico(),
        "cpf": gerar_cpf()
    }
    response = client.post("/clients/", json=cliente_data, headers=headers)
    assert response.status_code in [200, 201]
    cliente_id = response.json()["id"]

    response_get = client.get(f"/clients/{cliente_id}", headers=headers)
    assert response_get.status_code == 200
    assert response_get.json()["id"] == cliente_id

def test_atualizar_cliente():
    token = obter_token_admin()
    headers = {"Authorization": f"Bearer {token}"}

    cliente_data = {
        "nome": gerar_nome_unico(),
        "email": gerar_email_unico(),
        "cpf": gerar_cpf()
    }
    response = client.post("/clients/", json=cliente_data, headers=headers)
    cliente_id = response.json()["id"]

    novos_dados = {
        "nome": "Cliente Atualizado",
        "email": gerar_email_unico()
    }
    response_put = client.put(f"/clients/{cliente_id}", json=novos_dados, headers=headers)
    assert response_put.status_code == 200
    assert response_put.json()["nome"] == "Cliente Atualizado"

def test_deletar_cliente():
    token = obter_token_admin()
    headers = {"Authorization": f"Bearer {token}"}

    cliente_data = {
        "nome": gerar_nome_unico(),
        "email": gerar_email_unico(),
        "cpf": gerar_cpf()
    }
    response = client.post("/clients/", json=cliente_data, headers=headers)
    cliente_id = response.json()["id"]

    response_delete = client.delete(f"/clients/{cliente_id}", headers=headers)
    assert response_delete.status_code == 204

    # Verifica que não existe mais
    response_get = client.get(f"/clients/{cliente_id}", headers=headers)
    assert response_get.status_code == 404
