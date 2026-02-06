from fastapi import FastAPI, Depends
from .database import Base, engine, get_db
from .models import Apartment, Customer, Subscription

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

@app.post("/customers")
def create_customer(
    name: str,
    phone: str,
    apartment_id: int,
    flat_no: str,
    block: str | None = None,
    floor: int | None = None,
    address: str | None = None,
    db: Session = Depends(get_db),
):
    customer = Customer(
        name=name,
        phone=phone,
        apartment_id=apartment_id,
        flat_no=flat_no,
        block=block,
        floor=floor,
        address=address,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@app.get("/customers")
def get_customers(apartment_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Customer)
    if apartment_id is not None:
        query = query.filter(Customer.apartment_id == apartment_id)
    return query.all()

@app.post("/subscriptions")
def create_or_update_subscription(
    customer_id: int,
    milk_type: str,
    default_qty: float,
    price_per_liter: float,
    db: Session = Depends(get_db),
):
    existing = db.query(Subscription).filter(Subscription.customer_id == customer_id).first()

    if existing:
        existing.milk_type = milk_type
        existing.default_qty = default_qty
        existing.price_per_liter = price_per_liter
        db.commit()
        db.refresh(existing)
        return existing

    sub = Subscription(
        customer_id=customer_id,
        milk_type=milk_type,
        default_qty=default_qty,
        price_per_liter=price_per_liter,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

@app.get("/subscriptions/{customer_id}")
def get_subscription(customer_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.customer_id == customer_id).first()
    if not sub:
        return {"message": "No subscription found for this customer"}
    return sub
