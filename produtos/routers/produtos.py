from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from shared.dependencias import get_db
from produtos.models.produtos import Produto
from pydantic import BaseModel, Field
from datetime import date
from autenticacao.utils import verificar_token
from autenticacao.routers.autenticacao import get_current_user, admin_required

router = APIRouter(prefix="/products", tags=["Produtos"])

# Response model
class ProdutoOut(BaseModel):
    id: int
    descricao: str
    valor_venda: float
    codigo_barras: str
    secao: str
    estoque_inicial: int
    data_validade: Optional[str] = None
    imagem: Optional[str] = None
    disponivel: bool

    class Config:
        from_attributes = True

class ProdutoCreate(BaseModel):
    descricao: str
    valor_venda: float
    codigo_barras: str
    secao: str
    estoque_inicial: int
    data_validade: Optional[str] = None
    imagem: Optional[str] = None
    disponivel: bool = True

class ProdutoUpdate(BaseModel):
    descricao: Optional[str] = None
    valor_venda: Optional[float] = None
    codigo_barras: Optional[str] = None
    secao: Optional[str] = None
    estoque_inicial: Optional[int] = None
    data_validade: Optional[date] = None
    imagens: Optional[str] = None

@router.get(
    "/",
    response_model=List[ProdutoOut],
    dependencies=[Depends(verificar_token)],
    summary="Listar produtos",
    description="Retorna uma lista paginada de produtos com filtros opcionais como seção, faixa de preço e disponibilidade.",
    response_description="Lista de produtos filtrada",
)
def listar_produtos(
    skip: int = 0,
    limit: int = 10,
    secao: Optional[str] = Query(None, description="Filtrar produtos pela seção"),
    preco_min: Optional[float] = Query(None, description="Preço mínimo do produto"),
    preco_max: Optional[float] = Query(None, description="Preço máximo do produto"),
    disponivel: Optional[bool] = Query(None, description="Filtrar produtos disponíveis (true) ou indisponíveis (false)"),
    db: Session = Depends(get_db)
):
    query = db.query(Produto)

    if secao:
        query = query.filter(Produto.secao.ilike(f"%{secao}%"))
    if preco_min is not None:
        query = query.filter(Produto.valor_venda >= preco_min)
    if preco_max is not None:
        query = query.filter(Produto.valor_venda <= preco_max)
    if disponivel is not None:
        query = query.filter(Produto.disponivel == disponivel)

    produtos = query.offset(skip).limit(limit).all()
    return produtos

@router.post(
    "/",
    response_model=ProdutoOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
    summary="Criar novo produto",
    description="Adiciona um novo produto ao sistema, verificando se o código de barras é único.",
    responses={
        400: {"description": "Produto com código de barras já existe"},
        201: {"description": "Produto criado com sucesso"},
    }
)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    # Verifica se já existe um produto com o mesmo código de barras
    produto_existente = db.query(Produto).filter(Produto.codigo_barras == produto.codigo_barras).first()
    if produto_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto com este código de barras."
        )
    
    novo_produto = Produto(**produto.dict())
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

@router.get(
    "/{id}",
    response_model=ProdutoOut,
    dependencies=[Depends(verificar_token)],
    summary="Obter produto por ID",
    description="Retorna os detalhes de um produto pelo seu ID.",
    responses={
        404: {"description": "Produto não encontrado"},
        200: {"description": "Produto encontrado"},
    }
)
def obter_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )
    return produto

@router.put(
    "/{id}",
    response_model=ProdutoOut,
    dependencies=[Depends(admin_required)],
    summary="Atualizar produto",
    description="Atualiza os dados de um produto existente pelo ID.",
    responses={
        404: {"description": "Produto não encontrado"},
        200: {"description": "Produto atualizado com sucesso"},
    }
)
def atualizar_produto(
    id: int,
    produto_update: ProdutoUpdate,
    db: Session = Depends(get_db)
):
    produto = db.query(Produto).filter(Produto.id == id).first()

    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado."
        )

    for campo, valor in produto_update.dict(exclude_unset=True).items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)

    return produto

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
    summary="Deletar produto",
    description="Remove um produto do sistema pelo ID.",
    responses={
        404: {"description": "Produto não encontrado"},
        204: {"description": "Produto deletado com sucesso (sem conteúdo)"},
    }
)
def deletar_produto(id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(produto)
    db.commit()