import pytest
from app.exceptions import EntityNotFoundException


class TestOrderRepository:
    
    def test_create_order_success(self, repository, sample_order_data):
        order = repository.create(sample_order_data)
        assert order.id is not None
        assert order.customer_name == "Иван Петров"
        assert len(order.items) == 2
        expected_total = 1 * 50000.0 + 2 * 1500.0
        assert order.total_amount == expected_total
    
    def test_find_by_id_existing(self, repository, sample_order):
        found = repository.find_by_id(sample_order.id)
        assert found is not None
        assert found.id == sample_order.id
    
    def test_find_by_id_not_existing(self, repository):
        found = repository.find_by_id(99999)
        assert found is None
    
    @pytest.mark.parametrize("status", ["PENDING", "PAID"])
    def test_find_all_by_status(self, repository, status):
        for stat in ["PENDING", "PAID"]:
            data = {
                "customer_name": f"Тест {stat}",
                "delivery_address": "ул. Тестовая, 1",
                "status": stat,
                "items": [{"product_name": "Товар", "quantity": 1, "price": 100.0}]
            }
            repository.create(data)
        
        found = repository.find_all_by_status(status)
        assert len(found) >= 1
        for order in found:
            assert order.status == status
    
    def test_update_status_success(self, repository, sample_order):
        updated = repository.update_status(sample_order.id, "PAID")
        assert updated.status == "PAID"
    
    def test_update_status_not_existing(self, repository):
        with pytest.raises(EntityNotFoundException):
            repository.update_status(99999, "PAID")
    
    def test_delete_order_success(self, repository, sample_order):
        order_id = sample_order.id
        repository.delete(order_id)
        assert repository.find_by_id(order_id) is None
    
    def test_get_total_amount(self, repository, sample_order):
        total = repository.get_total_amount_for_order(sample_order.id)
        expected = sum(i.quantity * i.price for i in sample_order.items)
        assert total == expected
    
    def test_transaction_rollback(self, repository, db_session, sample_order_data):
        invalid_data = sample_order_data.copy()
        invalid_data["items"][0]["quantity"] = -1
        
        with pytest.raises(Exception):
            repository.create(invalid_data)
        
        from app.models import Order
        assert db_session.query(Order).count() == 0