from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from database import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base
from .enums import SubjectFieldEnum


class OpportunityRecommendation(Base):
    __tablename__ = "opportunity_recommendation"

    opportunity_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("registrations.user_id", ondelete="CASCADE"), nullable=True
    )
    subject_field = Column(
        Enum(SubjectFieldEnum, name="subject_field_enum"), nullable=False, index=True
    )
    external_media_url = Column(Text, nullable=False)
    source_platform = Column(String(100), nullable=False)
    media_description = Column(Text, nullable=False)
    opportunity_date = Column(DateTime, nullable=False)

    user = relationship("Registration", back_populates="opportunity_recommendations")
    
