from datetime import date as date_type
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class ContentPathwayCreate(BaseModel):
    content_id: int = Field(..., gt=0)
    external_media_url: HttpUrl
    media_description: str = Field(..., min_length=1, max_length=500)
    date: date_type

class ContentPathwayUpdate(BaseModel):
    external_media_url: Optional[HttpUrl] = None
    media_description: Optional[str] = Field(None, min_length=1, max_length=500)
    date: Optional[date_type] = None

class ContentPathwayResponse(BaseModel):
    content_pathway_id: int
    content_id: int
    external_media_url: str
    media_description: str
    date: date_type

    model_config = ConfigDict(from_attributes=True)