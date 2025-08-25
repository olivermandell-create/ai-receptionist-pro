from typing import Optional
from datetime import datetime, timedelta
from models import SessionLocal, Customer, Appointment

DEFAULT_SLOT_MINUTES = 30

def find_available_slot(tenant_id: int, when_text: Optional[str]):
    now = datetime.now()
    start = now + timedelta(hours=2)
    minute = 30 if start.minute >= 30 else 0
    start = start.replace(minute=minute, second=0, microsecond=0)
    return start

def _get_or_create_customer(db, tenant_id: int, name: str, phone: str):
    cust = db.query(Customer).filter(Customer.tenant_id==tenant_id, Customer.phone==phone).first()
    if not cust:
        cust = Customer(tenant_id=tenant_id, name=name, phone=phone)
        db.add(cust); db.flush()
    return cust

def create_appointment(tenant_id: int, phone: str, name: str, start_at: datetime, service_type: str):
    db = SessionLocal()
    try:
        end_at = start_at + timedelta(minutes=DEFAULT_SLOT_MINUTES)
        cust = _get_or_create_customer(db, tenant_id, name, phone)
        appt = Appointment(tenant_id=tenant_id, customer_id=cust.id, start_at=start_at, end_at=end_at, service_type=service_type, status="confirmed")
        db.add(appt); db.commit(); db.refresh(appt)
        return appt
    finally:
        db.close()

def cancel_appointment(tenant_id: int, phone: str, when_text: Optional[str]):
    db = SessionLocal()
    try:
        appt = db.query(Appointment).join(Customer).filter(
            Appointment.tenant_id==tenant_id, Customer.phone==phone, Appointment.status=="confirmed"
        ).order_by(Appointment.start_at.asc()).first()
        if not appt: return False
        appt.status = "canceled"; db.commit(); return True
    finally:
        db.close()

def reschedule_appointment(tenant_id: int, phone: str, from_when: Optional[str], to_when: Optional[str]):
    db = SessionLocal()
    try:
        appt = db.query(Appointment).join(Customer).filter(
            Appointment.tenant_id==tenant_id, Customer.phone==phone, Appointment.status=="confirmed"
        ).order_by(Appointment.start_at.asc()).first()
        if not appt: return False
        appt.start_at = appt.start_at + timedelta(days=1)
        appt.end_at = appt.end_at + timedelta(days=1)
        db.commit(); return True
    finally:
        db.close()
