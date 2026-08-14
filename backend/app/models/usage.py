from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Float
from datetime import datetime
from ..core.database import Base


class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    date = Column(String, nullable=False)  # YYYY-MM-DD
    files_processed = Column(Integer, default=0)
    bytes_processed = Column(BigInteger, default=0)
    processing_seconds = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)