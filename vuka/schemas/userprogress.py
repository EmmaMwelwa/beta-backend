from datetime import date
from pydantic import BaseModel
from typing import Optional, List

class UserProgressCreate(BaseModel):
   user_id: int
   assessment_id: int

class UserProgressResponse(BaseModel):
   progress_id: int
   user_id: int
   assessment_id: int
   score: Optional[int] = None
   streak_count: int

   model_config = {
      "from_attributes": True  
   }

class UserProgressUpdate(BaseModel):
   score: Optional[int] = None
   streak_count: Optional[int] = None

class CategoryScore(BaseModel):
   category: str
   average_score: int

class CompletedAssessment(BaseModel):
   category: str
   assessment_date: date
   score: int

class WeeklyActivityDay(BaseModel):
   weekday: str
   date: date
   completed: bool

class ProgressSummary(BaseModel):
   overall_progress: int
   category_breakdown: List[CategoryScore]
   current_streak: int
   weekly_activity: List[WeeklyActivityDay]
   completed_assessments: List[CompletedAssessment]

   model_config = {
      "from_attributes": True
   }