"""
Database setup for BizGenie AI
SQLite + SQLAlchemy for plan persistence
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'bizgenie.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class BusinessPlan(Base):
    __tablename__ = "business_plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    idea = Column(Text, nullable=False)
    plan_data = Column(JSON, nullable=True)  # Full plan as JSON
    status = Column(String(50), default="pending")  # pending, generating, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
