import pytest
from fastapi.testclient import TestClient
from main import app
from tests.utils import criar_token_admin, criar_produto_simples

client = TestClient(app)

@pytest.fixture
def token_admin():
    return criar_token_admin()

def test_criar_produto(token_admin):
    payload = {
        "nome": "Produto Teste",
        "codigo_barras": "1234567890123",
        "valor_venda": 25.5,
        "estoque_inicial": 50,
        "secao": "geral",
        "disponivel": True
    }
    response = client.post("/products/", json=payload, headers={"Authorization": f"Bearer {token_admin}"})
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == payload["nome"]
    assert data["codigo_barras"] == payload["codigo_barras"]

def test_listar_produtos(token_admin):
    response = client.get("/products/", headers={"Authorization": f"Bearer {token_admin}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_obter_produto_por_id(token_admin):
    produto = criar_produto_simples(token=token_admin)
    produto_id = produto["id"]

    response = client.get(f"/products/{produto_id}", headers={"Authorization": f"Bearer {token_admin}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == produto_id

def test_atualizar_produto(token_admin):
    produto = criar_produto_simples(token=token_admin)
    produto_id = produto["id"]

    update_payload = {
        "nome": "Produto Atualizado",
        "valor_venda": 30.0,
        "estoque_inicial": 80,
        "disponivel": False
    }
    response = client.put(f"/products/{produto_id}", json=update_payload, headers={"Authorization": f"Bearer {token_admin}"})
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == update_payload["nome"]
    assert data["valor_venda"] == update_payload["valor_venda"]
    assert data["disponivel"] == update_payload["disponivel"]

def test_deletar_produto(token_admin):
    produto = criar_produto_simples(token=token_admin)
    produto_id = produto["id"]

    response = client.delete(f"/products/{produto_id}", headers={"Authorization": f"Bearer {token_admin}"})
    assert response.status_code == 204
