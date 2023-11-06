from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from models import Base

class Entry(Base):

    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)

    description = Column(String(100), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
