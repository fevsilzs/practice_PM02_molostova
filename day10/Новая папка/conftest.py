import pytest
from fake_validator import FakeValidator

@pytest.fixture
def clean_validator():
    """Стандартный стабильный валидатор."""
    return FakeValidator(chaos_mode=False)

@pytest.fixture
def chaos_validator():
    """Валидатор в режиме хаоса для проверки устойчивости тестов."""
    return FakeValidator(chaos_mode=True)
