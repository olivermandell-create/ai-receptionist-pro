from models import init_db, SessionLocal, Tenant

init_db()
db = SessionLocal()
try:
    if not db.query(Tenant).first():
        t = Tenant(name="Demo Business", timezone="America/New_York", industry="general", phone="+15555550123", email="owner@example.com", hours_json="{}")
        db.add(t); db.commit()
        print("Seeded demo tenant with id=1 (map your Twilio number to 1 in NUMBER_TENANT_MAP).")
    else:
        print("Tenant already exists.")
finally:
    db.close()
