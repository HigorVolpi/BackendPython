from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr

from shared.dependencias import get_db
from shared.database import Base
from clientes.models.clientes import Cliente
from autenticacao.utils import verificar_token
from autenticacao.routers.autenticacao import get_current_user, admin_required

# router = APIRouter()
router = APIRouter(prefix="", tags=["Clientes"])



class ClienteOut(BaseModel):
    id: int
    nome: str
    email: str
    cpf: str

    class Config:
        from_attributes = True

class ClienteIn(BaseModel):
    nome: str
    email: EmailStr
    cpf: str

class ClienteUpdate(BaseModel):
    nome: Optional[str]
    email: Optional[EmailStr]
    cpf: Optional[str]  # Futuramente colocar uma validação de tamanho

    class Config:
        from_attributes = True


@router.get(
    "/",
    response_model=List[ClienteOut],
    dependencies=[Depends(verificar_token)],
    summary="Listar clientes",
    description="Retorna uma lista paginada de clientes, podendo filtrar por nome e email.",
    response_description="Lista de clientes",
)
def listar_clientes(
    skip: int = 0,
    limit: int = 10,
    nome: Optional[str] = Query(None, description="Filtro pelo nome do cliente"),
    email: Optional[str] = Query(None, description="Filtro pelo email do cliente"),
    db: Session = Depends(get_db)
):
    query = db.query(Cliente)

    if nome:
        query = query.filter(Cliente.nome.ilike(f"%{nome}%"))
    if email:
        query = query.filter(Cliente.email.ilike(f"%{email}%"))

    clientes = query.offset(skip).limit(limit).all()
    return clientes

@router.post(
    "/",
    response_model=ClienteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_required)],
    summary="Criar novo cliente",
    description="Cria um novo cliente. Email e CPF devem ser únicos.",
    responses={
        400: {"description": "Email ou CPF já cadastrado"},
        201: {"description": "Cliente criado com sucesso"},
    }
)
def criar_cliente(cliente: ClienteIn, db: Session = Depends(get_db)):
    # Verifica se email já existe
    if db.query(Cliente).filter(Cliente.email == cliente.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    # Verifica se CPF já existe
    if db.query(Cliente).filter(Cliente.cpf == cliente.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )

    novo_cliente = Cliente(**cliente.dict())
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente     

@router.get(
    "/{id}",
    response_model=ClienteOut,
    dependencies=[Depends(verificar_token)],
    summary="Buscar cliente por ID",
    description="Retorna os dados de um cliente pelo seu ID.",
    responses={
        404: {"description": "Cliente não encontrado"},
        200: {"description": "Cliente encontrado e retornado"},
    }
)
def get_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.put(
    "/{id}",
    response_model=ClienteUpdate,
    dependencies=[Depends(admin_required)],
    summary="Atualizar cliente",
    description="Atualiza os dados de um cliente existente pelo ID.",
    responses={
        404: {"description": "Cliente não encontrado"},
        200: {"description": "Cliente atualizado com sucesso"},
    }
)
def atualizar_cliente(id: int, dados: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    if dados.nome is not None:
        cliente.nome = dados.nome
    if dados.email is not None:
        cliente.email = dados.email
    if dados.cpf is not None:
        cliente.cpf = dados.cpf
    
    db.commit()
    db.refresh(cliente)
    return cliente

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)],
    summary="Deletar cliente",
    description="Remove um cliente pelo ID.",
    responses={
        404: {"description": "Cliente não encontrado"},
        204: {"description": "Cliente deletado com sucesso (sem conteúdo)"},
    }
)
def deletar_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    db.delete(cliente)
    db.commit()
    return