from sqlalchemy import Column, Integer, String, ForeignKey, Float
from .database import Base   # ← DOT IS IMPORTANT

class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, index=True)
    phone = Column(String, index=True)

    apartment_id = Column(Integer, ForeignKey("apartments.id"), index=True)

    block = Column(String, nullable=True)
    floor = Column(Integer, nullable=True)
    flat_no = Column(String, index=True)

    address = Column(String, nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, index=True)

    milk_type = Column(String, default="Cow")
    default_qty = Column(Float)          # e.g., 1.0
    price_per_liter = Column(Float)      # e.g., 60.0


