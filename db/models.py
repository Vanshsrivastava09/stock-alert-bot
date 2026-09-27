import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)
    last_price = Column(Float, nullable=True)
    in_stock = Column(Boolean, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    
    # Relationship to subscriptions
    subscriptions = relationship("Subscription", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, url='{self.url}', title='{self.title}', price={self.last_price}, in_stock={self.in_stock})>"


class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to product
    product = relationship("Product", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, chat_id='{self.chat_id}', product_id={self.product_id})>"


def init_db(db_path='stock_alerts.db'):
    # Check for DATABASE_URL environment variable (Render PostgreSQL)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Use PostgreSQL (Render)
        engine = create_engine(database_url)
    else:
        # Use SQLite (local development)
        engine = create_engine(f'sqlite:///{db_path}')
    
    Base.metadata.create_all(engine)
    return engine
