from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from datetime import datetime
from ..core.database import Base


class Conversion(Base):
    __tablename__ = "conversions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    converter = Column(String, nullable=False)
    source_format = Column(String, nullable=True)
    target_format = Column(String, nullable=True)

    options = Column(JSON, default=dict)
    processing_time = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)