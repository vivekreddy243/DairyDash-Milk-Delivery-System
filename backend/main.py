from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import date
import calendar
from typing import List

from .schemas import DeliveryCreate, DeliveryOut
from .schemas import CustomerCreate, CustomerOut
from .schemas import SubscriptionCreate, SubscriptionOut
from .schemas import ApartmentCreate, ApartmentOut
from .schemas import CustomerMonthlyBillOut, ApartmentMonthlyBillOut

from .database import Base, engine, get_db
from .models import Apartment, Customer, Subscription, DailyDelivery



app = FastAPI(title="DairyDash API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "service": "DairyDash API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/apartments", response_model=List[ApartmentOut])
def get_apartments(db: Session = Depends(get_db)):
    return db.query(Apartment).all()

@app.post("/customers", response_model=CustomerOut)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer



@app.get("/customers", response_model=List[CustomerOut])
def get_customers(apartment_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Customer)
    if apartment_id is not None:
        query = query.filter(Customer.apartment_id == apartment_id)
    return query.all()


@app.post("/subscriptions", response_model=SubscriptionOut)
def create_or_update_subscription(payload: SubscriptionCreate, db: Session = Depends(get_db)):
    existing = db.query(Subscription).filter(Subscription.customer_id == payload.customer_id).first()

    if existing:
        existing.milk_type = payload.milk_type
        existing.default_qty = payload.default_qty
        existing.price_per_liter = payload.price_per_liter
        db.commit()
        db.refresh(existing)
        return existing

    sub = Subscription(**payload.model_dump())
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

@app.get("/subscriptions/{customer_id}", response_model=SubscriptionOut | dict)
def get_subscription(customer_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.customer_id == customer_id).first()
    if not sub:
        return {"message": "No subscription found for this customer"}
    return sub


@app.post("/deliveries", response_model=DeliveryOut)
def create_delivery(payload: DeliveryCreate, db: Session = Depends(get_db)):
    d = payload.model_dump()

    # default date if not provided
    if d["delivery_date"] is None:
        d["delivery_date"] = date.today()

    # default qty from subscription if not provided
    if d["quantity"] is None:
        sub = db.query(Subscription).filter(Subscription.customer_id == d["customer_id"]).first()
        if not sub:
            return {"error": "No subscription found for customer"}
        d["quantity"] = sub.default_qty

    delivery = DailyDelivery(**d)
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery



@app.get("/deliveries", response_model=List[DeliveryOut])
def get_deliveries(
    delivery_date: date | None = None,
    customer_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(DailyDelivery)

    if delivery_date is not None:
        q = q.filter(DailyDelivery.delivery_date == delivery_date)

    if customer_id is not None:
        q = q.filter(DailyDelivery.customer_id == customer_id)

    return q.all()



@app.get("/billing/{customer_id}", response_model=CustomerMonthlyBillOut)
def get_monthly_bill(customer_id: int, year: int, month: int, db: Session = Depends(get_db)):
    if month < 1 or month > 12:
        return {"error": "month must be between 1 and 12"}

    sub = db.query(Subscription).filter(Subscription.customer_id == customer_id).first()
    if not sub:
        return {"error": "No subscription found for customer"}

    last_day = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    deliveries = (
        db.query(DailyDelivery)
        .filter(DailyDelivery.customer_id == customer_id)
        .filter(DailyDelivery.delivery_date >= start_date)
        .filter(DailyDelivery.delivery_date <= end_date)
        .all()
    )

    # Separate delivered and skipped deliveries
    delivered = [d for d in deliveries if d.status == "Delivered"]
    skipped = [d for d in deliveries if d.status == "Skipped"]

    total_liters = sum(d.quantity for d in delivered)
    total_amount = total_liters * sub.price_per_liter

    return {
        "customer_id": customer_id,
        "year": year,
        "month": month,
        "price_per_liter": sub.price_per_liter,
        "total_liters": total_liters,
        "total_amount": total_amount,
        "delivered_days": len(delivered),
        "skipped_days": len(skipped),
        "records_found": len(deliveries),
    }



@app.get("/billing/apartment/{apartment_id}", response_model=ApartmentMonthlyBillOut)

def get_apartment_monthly_bill(apartment_id: int, year: int, month: int, db: Session = Depends(get_db)):
    if month < 1 or month > 12:
        return {"error": "month must be between 1 and 12"}

    last_day = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    customers = db.query(Customer).filter(Customer.apartment_id == apartment_id).all()

    results = []
    apartment_total = 0.0

    for c in customers:
        sub = db.query(Subscription).filter(Subscription.customer_id == c.id).first()
        if not sub:
            continue

        deliveries = (
            db.query(DailyDelivery)
            .filter(DailyDelivery.customer_id == c.id)
            .filter(DailyDelivery.delivery_date >= start_date)
            .filter(DailyDelivery.delivery_date <= end_date)
            .all()
        )

        delivered = [d for d in deliveries if d.status == "Delivered"]
        liters = sum(d.quantity for d in delivered)
        amount = liters * sub.price_per_liter

        apartment_total += amount

        results.append({
            "customer_id": c.id,
            "name": c.name,
            "flat_no": c.flat_no,
            "liters": liters,
            "amount": amount,
        })

    return {
        "apartment_id": apartment_id,
        "year": year,
        "month": month,
        "customers": results,
        "apartment_total": apartment_total,
    }

