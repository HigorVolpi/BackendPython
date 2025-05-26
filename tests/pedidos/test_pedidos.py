import pytest
from fastapi.testclient import TestClient
from main import app
from tests.utils import criar_token_admin, criar_cliente_com_dados, criar_produto_simples

client = TestClient(app)

@pytest.fixture
def token_admin():
    return criar_token_admin()

@pytest.fixture
def cliente_id(token_admin):
    cliente = criar_cliente_com_dados(token=token_admin)
    return cliente

@pytest.fixture
def produto_id(token_admin):
    produto = criar_produto_simples(token=token_admin)
    return produto

def test_criar_pedido(token_admin, cliente_id, produto_id):
    payload = {
        "cliente_id": cliente_id["id"],
        "produtos": [
            {"produto_id": produto_id["id"], "quantidade": 1}
        ]
    }
    response = client.post("/orders/", json=payload, headers={"Authorization": f"Bearer {token_admin}"})
    print("test_criar_pedido status:", response.status_code)
    print("test_criar_pedido response:", response.json())
    assert response.status_code == 201
    assert response.json()["status"] == "pendente"
    assert response.json()["cliente_id"] == cliente_id["id"]

def test_listar_pedidos(token_admin):
    response = client.get("/orders/", headers={"Authorization": f"Bearer {token_admin}"})
    print("test_listar_pedidos status:", response.status_code)
    print("test_listar_pedidos response:", response.json())
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_obter_pedido_por_id(token_admin, cliente_id, produto_id):
    payload = {
        "cliente_id": cliente_id["id"],
        "produtos": [
            {"produto_id": produto_id["id"], "quantidade": 1}
        ]
    }
    response = client.post("/orders/", json=payload, headers={"Authorization": f"Bearer {token_admin}"})
    pedido = response.json()
    pedido_id = pedido["id"]

    res = client.get(f"/orders/{pedido_id}", headers={"Authorization": f"Bearer {token_admin}"})
    print("test_obter_pedido_por_id status:", res.status_code)
    print("test_obter_pedido_por_id response:", res.json())
    assert res.status_code == 200
    assert res.json()["id"] == pedido_id

def test_atualizar_status_pedido(token_admin, cliente_id, produto_id):
    payload = {
        "cliente_id": cliente_id["id"],
        "produtos": [
            {"produto_id": produto_id["id"], "quantidade": 1}
        ]
    }
    response = client.post("/orders/", json=payload, headers={"Authorization": f"Bearer {token_admin}"})
    pedido_id = response.json()["id"]

    update = {"status": "enviado"}
    res = client.put(f"/orders/{pedido_id}", json=update, headers={"Authorization": f"Bearer {token_admin}"})
    print("test_atualizar_status_pedido status:", res.status_code)
    print("test_atualizar_status_pedido response:", res.json())
    assert res.status_code == 200
    assert res.json()["status"] == "enviado"

def test_deletar_pedido(token_admin, cliente_id, produto_id):
    payload = {
        "cliente_id": cliente_id["id"],
        "produtos": [
            {"produto_id": produto_id["id"], "quantidade": 1}
        ]
    }
    response = client.post("/orders/", json=payload, headers={"Authorization": f"Bearer {token_admin}"})
    pedido_id = response.json()["id"]

    res = client.delete(f"/orders/{pedido_id}", headers={"Authorization": f"Bearer {token_admin}"})
    print("test_deletar_pedido status:", res.status_code)
    assert res.status_code == 204
