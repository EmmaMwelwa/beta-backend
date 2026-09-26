from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class VerifiedAssessment(Base):
    __tablename__ = "verified_assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registrations.user_id"), nullable=False)
    category = Column(String(50), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    generated_assessment_id = Column(Integer,ForeignKey("generated_assessment.generated_assessment_id"),nullable=False)


    user_progress = relationship("UserProgress", back_populates="assessment")
    registration = relationship("Registration", back_populates="verified_assessments")
    generated_assessment = relationship("GeneratedAssessment",back_populates="verified_assessments")
    
