from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from shared.database import Base
from produtos.models.produtos import Produto  # Importa o Produto

class PedidoProduto(Base):
    __tablename__ = "pedido_produto"

    pedido_id = Column(Integer, ForeignKey('pedidos.id'), primary_key=True)
    produto_id = Column(Integer, ForeignKey('produtos.id'), primary_key=True)
    quantidade = Column(Integer, nullable=False, default=1)

    pedido = relationship("Pedido", back_populates="pedido_produtos")
    produto = relationship("Produto", back_populates="pedido_produtos")


class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    status = Column(String, nullable=False, default='pendente')
    data_criacao = Column(DateTime, default=datetime.utcnow)

    cliente = relationship('Cliente', back_populates="pedidos")
    pedido_produtos = relationship('PedidoProduto', back_populates='pedido', cascade="all, delete-orphan")
