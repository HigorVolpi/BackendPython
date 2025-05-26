from sqlalchemy import Column, Integer, String

from shared.database import Base

class Tabela_Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_usuario = Column(String, unique=True)
    senha = Column(String)
    papel = Column(String) # admin, usuario