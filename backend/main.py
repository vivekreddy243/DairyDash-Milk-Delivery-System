from fastapi import FastAPI, Depends
from .database import Base, engine, get_db
from .models import Apartment

from sqlalchemy.orm import Session



app = FastAPI(title="DairyDash API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "DairyDash backend is running"}


@app.get("/apartments")
def get_apartments(db: Session = Depends(get_db)):
    return db.query(Apartment).all()


@app.post("/apartments")
def create_apartment(name: str, db: Session = Depends(get_db)):
    apartment = Apartment(name=name)
    db.add(apartment)
    db.commit()
    db.refresh(apartment)
    return apartment
