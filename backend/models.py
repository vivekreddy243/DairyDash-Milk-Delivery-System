from sqlalchemy import Column, Integer, String
from .database import Base   # ← DOT IS IMPORTANT

class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
