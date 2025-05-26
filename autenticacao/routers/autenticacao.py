from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from shared.dependencias import get_db
from autenticacao.models.autenticacao import Tabela_Usuarios

router = APIRouter(prefix="/auth")

# "Banco de dados" simples em memória
usuarios_cadastrados = {}

# Configurações do JWT
SECRET_KEY = "minha_chave_super_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class Usuario(BaseModel):
    nome_usuario: str
    senha: str
    papel: str # admin, user

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nome_usuario: str = payload.get("sub")
        papel: str = payload.get("papel")
        if nome_usuario is None or papel is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        return {"nome_usuario": nome_usuario, "papel": papel}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    
def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user["papel"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: admin necessário"
        )
    return current_user

@router.post(
    "/register",
    summary="Registrar novo usuário",
    description="Cria um novo usuário no sistema, garantindo que o nome de usuário seja único.",
    status_code=201,
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"description": "Usuário já existe"}
    }
)
def register(usuario_cadastrado: Usuario, db: Session = Depends(get_db)):
    usuario_existente = db.query(Tabela_Usuarios).filter(Tabela_Usuarios.nome_usuario == usuario_cadastrado.nome_usuario).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_usuario = Tabela_Usuarios(
        nome_usuario=usuario_cadastrado.nome_usuario,
        senha=usuario_cadastrado.senha,
        papel=usuario_cadastrado.papel
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"msg": "Usuário criado com sucesso"}


@router.post(
    "/login",
    summary="Login de usuário",
    description="Autentica usuário e retorna token JWT para autenticação nas rotas protegidas.",
    response_model=Token,
    responses={
        200: {"description": "Login realizado com sucesso"},
        401: {"description": "Usuário ou senha incorretos"}
    }
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Tabela_Usuarios).filter(Tabela_Usuarios.nome_usuario == form_data.username).first()

    if not usuario or usuario.senha != form_data.password:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    access_token = create_access_token(
        data={"sub": usuario.nome_usuario, "papel": usuario.papel},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/refresh-token",
    summary="Atualizar token JWT",
    description="Gera um novo token JWT válido, prolongando o tempo de sessão do usuário autenticado.",
    response_model=Token,
)
def refresh_token(current_user: dict = Depends(get_current_user)):
    novo_token = create_access_token(
        data={"sub": current_user["nome_usuario"], "papel": current_user["papel"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": novo_token, "token_type": "bearer"}
