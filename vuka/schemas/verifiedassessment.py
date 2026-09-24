from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Optional, Any

class VerifiedAssessmentCreate(BaseModel):
    user_id: int
    generated_assessment_id: int
    category: str
    score: int = 0

class AssessmentProgress(str, Enum):
    in_progress = "in_progress"
    completed = "completed"

class VerifiedAssessmentResponse(BaseModel):
    assessment_id: int
    user_id: int
    category: str
    score: int
    assessment_date: datetime

    model_config = {
        "from_attributes": True
    }

class AssessmentSubmission(BaseModel):
    user_id: int
    assessment_id: int
    answers: list[dict[str, Any]]

class VerifiedAssessmentUpdate(BaseModel):
    category: Optional[str] = None
    score: Optional[int] = None


class AssessmentsDelete(BaseModel):
    assessment_id: int