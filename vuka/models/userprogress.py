from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    progress_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("registrations.user_id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("verified_assessments.assessment_id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=True)
    streak_count = Column(Integer, default=0)

    registration = relationship("Registration", back_populates="user_progress")
    assessment = relationship("VerifiedAssessment", back_populates="user_progress")




