from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import os

from app.models import Base


class Database:
    """Класс для управления подключением к базе данных"""
    
    def __init__(self, database_url: Optional[str] = None):
        if database_url is None:
            # По умолчанию используем SQLite
            database_url = "sqlite:///./orders.db"
        
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Создает все таблицы в базе данных"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Удаляет все таблицы из базы данных"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Возвращает новую сессию"""
        return self.SessionLocal()
    
    def __enter__(self):
        self.session = self.get_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
