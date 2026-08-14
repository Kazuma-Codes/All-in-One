from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    extension = Column(String, nullable=True)

    size = Column(BigInteger, default=0)
    checksum = Column(String, nullable=True)
    storage_key = Column(String, nullable=False, unique=True)

    status = Column(String, default="PENDING")  # PENDING, UPLOADED, DELETED, EXPIRED

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="files")