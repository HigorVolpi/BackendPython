from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from shared.dependencias import get_db
from pedidos.models.pedidos import Pedido, PedidoProduto
from clientes.models.clientes import Cliente
from produtos.models.produtos import Produto
from autenticacao.utils import verificar_token
from autenticacao.routers.autenticacao import get_current_user, admin_required

from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["Pedidos"])

# Schemas Pydantic para entrada e saída
class ProdutoPedido(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    cliente_id: int
    produtos: List[ProdutoPedido]

class PedidoUpdate(BaseModel):
    status: Optional[str]

class PedidoOut(BaseModel):
    id: int
    cliente_id: int
    status: str
    data_criacao: datetime
    produtos: List[ProdutoPedido]

    class Config:
        from_attributes = True


@router.get(
    "/",
    response_model=List[PedidoOut],
    dependencies=[Depends(verificar_token)],
    summary="Listar pedidos",
    description=(
        "Retorna a lista de pedidos, com filtros opcionais por ID do pedido, "
        "ID do cliente, status, seção dos produtos, e intervalo de datas."
    ),
    response_description="Lista de pedidos filtrados",
)
def listar_pedidos(
    id_pedido: Optional[int] = Query(None, description="ID específico do pedido"),
    cliente_id: Optional[int] = Query(None, description="ID do cliente"),
    status: Optional[str] = Query(None, description="Status do pedido"),
    secao: Optional[str] = Query(None, description="Seção dos produtos no pedido"),
    data_inicio: Optional[datetime] = Query(None, description="Data inicial do pedido (inclusive)"),
    data_fim: Optional[datetime] = Query(None, description="Data final do pedido (inclusive)"),
    db: Session = Depends(get_db)
):
    query = db.query(Pedido)

    if id_pedido:
        query = query.filter(Pedido.id == id_pedido)
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if status:
        query = query.filter(Pedido.status.ilike(f"%{status}%"))
    if data_inicio:
        query = query.filter(Pedido.data_criacao >= data_inicio)
    if data_fim:
        query = query.filter(Pedido.data_criacao <= data_fim)
    if secao:
        # Filtro pela seção dos produtos do pedido
        query = query.join(Pedido.produtos).filter(Produto.secao.ilike(f"%{secao}%"))

    pedidos = query.all()
    return pedidos


@router.post(
    "/",
    response_model=PedidoOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
    summary="Criar pedido",
    description="Cria um novo pedido verificando se o cliente existe e se há estoque suficiente para os produtos.",
    responses={
        201: {"description": "Pedido criado com sucesso"},
        400: {"description": "Estoque insuficiente para algum produto"},
        404: {"description": "Cliente ou produto não encontrado"},
    },
)
def criar_pedido(pedido_in: PedidoCreate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == pedido_in.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    produtos_pedido = []
    for item in pedido_in.produtos:
        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")
        if produto.estoque_inicial is None or produto.estoque_inicial < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para produto {produto.id}")
        produtos_pedido.append((produto, item.quantidade))

    novo_pedido = Pedido(cliente_id=pedido_in.cliente_id, status='pendente')
    db.add(novo_pedido)
    db.flush()  # Para gerar id do pedido

    for produto, quantidade in produtos_pedido:
        # Atualizar estoque
        produto.estoque_inicial -= quantidade
        # Inserir na tabela associativa
        stmt = PedidoProduto.insert().values(pedido_id=novo_pedido.id, produto_id=produto.id, quantidade=quantidade)
        db.execute(stmt)

    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido


@router.get(
    "/{id}",
    response_model=PedidoOut,
    dependencies=[Depends(verificar_token)],
    summary="Obter pedido por ID",
    description="Retorna os detalhes de um pedido específico pelo seu ID.",
    responses={
        404: {"description": "Pedido não encontrado"},
        200: {"description": "Pedido encontrado"},
    },
)
def obter_pedido(id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.put(
    "/{id}",
    response_model=PedidoOut,
    dependencies=[Depends(admin_required)],
    summary="Atualizar pedido",
    description="Atualiza o status de um pedido pelo ID.",
    responses={
        404: {"description": "Pedido não encontrado"},
        200: {"description": "Pedido atualizado com sucesso"},
    },
)
def atualizar_pedido(id: int, pedido_in: PedidoUpdate, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido_in.status:
        pedido.status = pedido_in.status
    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
    summary="Deletar pedido",
    description="Remove um pedido pelo ID.",
    responses={
        404: {"description": "Pedido não encontrado"},
        204: {"description": "Pedido deletado com sucesso"},
    },
)
def deletar_pedido(id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    db.delete(pedido)
    db.commit()
    return
