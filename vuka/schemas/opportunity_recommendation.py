from __future__ import annotations
from datetime import datetime as Datetime
from pydantic import BaseModel, ConfigDict, Field
from vuka.models.enums import SubjectFieldEnum



class OpportunityRecommendationBase(BaseModel):
    user_id: int | None = Field(
        None, description="Null while the opportunity sits unassigned in the pool"
    )
    subject_field: SubjectFieldEnum
    external_media_url: str
    source_platform: str = Field(..., max_length=100)
    media_description: str
    opportunity_date: Datetime


class OpportunityRecommendationCreate(OpportunityRecommendationBase):
    pass


class OpportunityRecommendationUpdate(BaseModel):
    user_id: int | None = Field(None, description="Set this to assign a pool item to a user (optional)")
    subject_field: SubjectFieldEnum | None = Field(None, description="Update the subject field (optional)")
    external_media_url: str | None = Field(None, description="Update the external media URL (optional)")
    source_platform: str | None = Field(None, description="Update the source platform (optional)", max_length=100)
    media_description: str | None = Field(None, description="Update the media description (optional)")
    opportunity_date: Datetime | None = Field(None, description="Update the opportunity date (optional)")


class OpportunityRecommendationRead(OpportunityRecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    opportunity_id: int


class OpportunitySubjectFetchRequest(BaseModel):
    subject_field: SubjectFieldEnum
    query: str | None = Field(
        None,
        min_length=3,
        description="Custom search query. If omitted, a sensible default for the subject field is used.",
    )
    num_results: int = Field(10, ge=1, le=20)