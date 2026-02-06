from pydantic import BaseModel
from datetime import date
from typing import Optional


# ---------- Apartments ----------
class ApartmentCreate(BaseModel):
    name: str


class ApartmentOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# ---------- Customers ----------
class CustomerCreate(BaseModel):
    name: str
    phone: str
    apartment_id: int
    flat_no: str
    block: Optional[str] = None
    floor: Optional[int] = None
    address: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    apartment_id: int
    flat_no: str
    block: Optional[str] = None
    floor: Optional[int] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Subscriptions ----------
class SubscriptionCreate(BaseModel):
    customer_id: int
    milk_type: str
    default_qty: float
    price_per_liter: float


class SubscriptionOut(BaseModel):
    id: int
    customer_id: int
    milk_type: str
    default_qty: float
    price_per_liter: float

    class Config:
        from_attributes = True


# ---------- Deliveries ----------
class DeliveryCreate(BaseModel):
    customer_id: int
    delivery_date: Optional[date] = None
    quantity: Optional[float] = None
    status: str = "Delivered"


class DeliveryOut(BaseModel):
    id: int
    customer_id: int
    delivery_date: date
    quantity: float
    status: str

    class Config:
        from_attributes = True
