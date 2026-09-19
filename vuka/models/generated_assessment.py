from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base



class GeneratedAssessment(Base):

    __tablename__ = "generated_assessment"

    generated_assessment_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer,ForeignKey("content.content_id"),nullable=False,unique=True,
        index=True,
    )
    category = Column(String(50), nullable=False)
    questions = Column(Text, nullable=False)
    model_used = Column(String(50), nullable=False, default="gemini-2.5-flash")
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    content = relationship("Content", back_populates="generated_assessment")