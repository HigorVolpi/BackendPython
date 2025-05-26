from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from shared.database import Base
from sqlalchemy.orm import relationship

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descricao = Column(String, nullable=False)
    valor_venda = Column(Float, nullable=False)
    codigo_barras = Column(String, unique=True, nullable=False)
    secao = Column(String, nullable=False)
    estoque_inicial = Column(Integer, nullable=False)
    data_validade = Column(Date, nullable=True)  # opcional
    imagem = Column(String, nullable=True)       # pode ser uma URL ou nome do arquivo
    disponivel = Column(Boolean, default=True)
    pedido_produtos = relationship('PedidoProduto', back_populates='produto')
