from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    input_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    output_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)

    operation = Column(String, nullable=False)
    status = Column(String, default="QUEUED")
    progress = Column(Integer, default=0)

    error_message = Column(String, nullable=True)
    options = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="jobs")
    input_file = relationship("File", foreign_keys=[input_file_id])
    output_file = relationship("File", foreign_keys=[output_file_id])