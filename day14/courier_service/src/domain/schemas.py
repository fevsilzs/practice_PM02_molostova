# src/domain/schemas.py

from pydantic import BaseModel, Field
from typing import Optional

class AddressSchema(BaseModel):
    street: str = Field(..., min_length=2, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., pattern=r'^\d{5,6}$')  # <-- pattern, НЕ regex!
    country: str = Field(default="Russia", min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    class Config:
        json_schema_extra = {
            "example": {
                "street": "ул. Ленина, 10",
                "city": "Москва",
                "postal_code": "101000",
                "country": "Russia",
                "latitude": 55.7558,
                "longitude": 37.6173
            }
        }

class OrderCreateSchema(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')  # <-- pattern, НЕ regex!
    pickup: AddressSchema
    delivery: AddressSchema

    class Config:
        json_schema_extra = {
            "example": {
                "customer_name": "Иван Петров",
                "customer_phone": "+79111234567",
                "pickup": {
                    "street": "ул. Тверская, 1",
                    "city": "Москва",
                    "postal_code": "101000",
                    "country": "Russia",
                    "latitude": 55.7558,
                    "longitude": 37.6173
                },
                "delivery": {
                    "street": "ул. Арбат, 20",
                    "city": "Москва",
                    "postal_code": "119002",
                    "country": "Russia",
                    "latitude": 55.7516,
                    "longitude": 37.6189
                }
            }
        }

class CourierCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,15}$')  # <-- pattern, НЕ regex!
    max_orders: int = Field(3, ge=1, le=10)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Алексей Курьер",
                "phone": "+79119876543",
                "max_orders": 3
            }
        }

class OrderUpdateStatusSchema(BaseModel):
    status: str = Field(..., pattern=r'^(pending|assigned|in_progress|delivered|cancelled)$')  # <-- pattern, НЕ regex!

    class Config:
        json_schema_extra = {
            "example": {
                "status": "delivered"
            }
        }
