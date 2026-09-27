import os
from sqlalchemy.orm import sessionmaker
from db.models import Product, Subscription, Base, init_db
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path='stock_alerts.db'):
        # Check for DATABASE_URL environment variable (Render PostgreSQL)
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            self.engine = init_db()  # Will use DATABASE_URL
        else:
            self.engine = init_db(db_path)  # Will use SQLite
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
    
    def add_product_if_new(self, url, title=None):
        session = self.get_session()
        try:
            existing_product = session.query(Product).filter_by(url=url).first()
            if existing_product:
                return existing_product
            
            new_product = Product(url=url, title=title)
            session.add(new_product)
            session.commit()
            session.refresh(new_product)
            return new_product
        finally:
            session.close()
    
    def get_all_products(self):
        session = self.get_session()
        try:
            products = session.query(Product).all()
            return products
        finally:
            session.close()
    
    def update_product_status(self, product_id, price=None, in_stock=None):
        session = self.get_session()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                return None
            
            if price is not None:
                product.last_price = price
            if in_stock is not None:
                product.in_stock = in_stock
            
            product.last_checked_at = datetime.utcnow()
            session.commit()
            session.refresh(product)
            return product
        finally:
            session.close()
    
    def subscribe(self, chat_id, product_id):
        session = self.get_session()
        try:
            # Check if already subscribed
            existing = session.query(Subscription).filter_by(
                chat_id=chat_id, 
                product_id=product_id
            ).first()
            
            if existing:
                return existing
            
            # Verify product exists
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                return None
            
            new_subscription = Subscription(chat_id=chat_id, product_id=product_id)
            session.add(new_subscription)
            session.commit()
            session.refresh(new_subscription)
            return new_subscription
        finally:
            session.close()
    
    def get_subscribers_for_product(self, product_id):
        session = self.get_session()
        try:
            subscriptions = session.query(Subscription).filter_by(product_id=product_id).all()
            return [sub.chat_id for sub in subscriptions]
        finally:
            session.close()
    
    def unsubscribe(self, chat_id, product_id):
        session = self.get_session()
        try:
            subscription = session.query(Subscription).filter_by(
                chat_id=chat_id,
                product_id=product_id
            ).first()
            
            if subscription:
                session.delete(subscription)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_product_by_url(self, url):
        session = self.get_session()
        try:
            product = session.query(Product).filter_by(url=url).first()
            return product
        finally:
            session.close()
    
    def get_product_by_id(self, product_id):
        session = self.get_session()
        try:
            product = session.query(Product).filter_by(id=product_id).first()
            return product
        finally:
            session.close()
