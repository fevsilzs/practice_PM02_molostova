import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.repositories import OrderRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def repository(db_session):
    return OrderRepository(db_session)


@pytest.fixture
def sample_order_data():
    return {
        "customer_name": "Иван Петров",
        "delivery_address": "г. Москва, ул. Тверская, д. 1",
        "items": [
            {"product_name": "Ноутбук", "quantity": 1, "price": 50000.0},
            {"product_name": "Мышь", "quantity": 2, "price": 1500.0},
        ]
    }


@pytest.fixture
def sample_order(repository, sample_order_data):
    return repository.create(sample_order_data)