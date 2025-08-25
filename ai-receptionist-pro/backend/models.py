import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_receptionist.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Tenant(Base):
    __tablename__ = "tenant"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    timezone = Column(String, default="America/New_York")
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    hours_json = Column(Text, default="{}")
    faq = Column(Text, default="")

    appointments = relationship("Appointment", back_populates="tenant")

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True)

    appointments = relationship("Appointment", back_populates="customer")

class Appointment(Base):
    __tablename__ = "appointment"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    service_type = Column(String, default="appointment")
    status = Column(String, default="confirmed")

    tenant = relationship("Tenant", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")

def init_db():
    Base.metadata.create_all(bind=engine)
