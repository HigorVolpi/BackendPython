# API de Gerenciamento de Clientes, Produtos e Pedidos

## Visão Geral

Esta API foi desenvolvida utilizando FastAPI para gerenciar clientes, produtos e pedidos de forma segura e eficiente.  
Possui autenticação via JWT e controle de acesso baseado em papéis (usuário comum e administrador).

---

## Documentação Automática (Swagger)

A API possui documentação automática acessível via Swagger UI, que é gerada dinamicamente pelo FastAPI.  
Você pode acessar a documentação interativa para testar os endpoints e visualizar os modelos, parâmetros e respostas.

**URL da documentação:**  
`http://<host>:<porta>/docs`

---

## Endpoints Principais

### Autenticação

- `POST /register`  
  Registra um novo usuário. Verifica se o nome de usuário já existe.

- `POST /login`  
  Realiza login e retorna token JWT para acesso autenticado.

- `POST /refresh-token`  
  Renova o token JWT para manter a sessão ativa.

---

### Clientes

- `GET /clientes/`  
  Lista clientes com filtros opcionais por nome e email. Requer autenticação.

- `POST /clientes/`  
  Cria um novo cliente. Requer permissão de administrador.

- `GET /clientes/{id}`  
  Obtém informações de um cliente específico pelo ID. Requer autenticação.

- `PUT /clientes/{id}`  
  Atualiza dados do cliente. Requer permissão de administrador.

- `DELETE /clientes/{id}`  
  Remove um cliente pelo ID. Requer permissão de administrador.

---

### Produtos

- `GET /produtos/`  
  Lista produtos com filtros como seção, faixa de preço e disponibilidade. Requer autenticação.

- `POST /produtos/`  
  Cria um novo produto. Verifica duplicidade por código de barras. Requer permissão de administrador.

- `GET /produtos/{id}`  
  Obtém detalhes de um produto específico. Requer autenticação.

- `PUT /produtos/{id}`  
  Atualiza dados do produto. Requer permissão de administrador.

- `DELETE /produtos/{id}`  
  Remove um produto pelo ID. Requer permissão de administrador.

---

### Pedidos

- `GET /orders/`  
  Lista pedidos com filtros como ID, cliente, status, seção e intervalo de datas. Requer autenticação.

- `POST /orders/`  
  Cria um novo pedido para um cliente. Valida estoque dos produtos e atualiza-o. Requer permissão de administrador.

- `GET /orders/{id}`  
  Obtém um pedido específico pelo ID. Requer autenticação.

- `PUT /orders/{id}`  
  Atualiza o status do pedido. Requer permissão de administrador.

- `DELETE /orders/{id}`  
  Remove um pedido pelo ID. Requer permissão de administrador.

---

## Como Executar

1. Clone o repositório  
2. Configure o ambiente Python e instale as dependências com `pip install -r requirements.txt`  
3. Configure variáveis de ambiente para JWT e banco de dados  
4. Execute a aplicação com `uvicorn main:app --reload`  
5. Acesse a documentação em `http://localhost:8000/docs`

---

## Testes

Os testes automatizados são implementados com pytest e cobrem as principais rotas e casos de uso.  
Para rodar os testes:  
```bash
pytest
