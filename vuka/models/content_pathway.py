from sqlalchemy import Column, Date, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from database import Base

class ContentPathway(Base):
    __tablename__ = "content_pathway"

    content_pathway_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("registrations.user_id"),nullable=False,index=True)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False, index=True)
    external_media_url = Column(Text, nullable=False)
    media_description = Column(Text, nullable=False)
    date = Column(Date, nullable=False, index=True)

    content = relationship("Content", back_populates="content_pathway")
    user = relationship("Registration", back_populates="content_pathways")