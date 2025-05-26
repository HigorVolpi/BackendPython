from fastapi import HTTPException, Depends, APIRouter
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

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        papel = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Usuário não autenticado")
        usuario = usuarios_cadastrados.get(username)
        if usuario is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        return {"nome_usuario": username, "papel": papel}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/register")
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

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Tabela_Usuarios).filter(Tabela_Usuarios.nome_usuario == form_data.username).first()

    if not usuario or usuario.senha != form_data.password:
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")

    token_data = {
        "sub": usuario.nome_usuario,
        "role": usuario.papel,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=Token)
def refresh_token(current_user: dict = Depends(get_current_user)):
    novo_token = create_access_token(
        data={"sub": current_user["nome_usuario"], "role": current_user["papel"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": novo_token, "token_type": "bearer"}
