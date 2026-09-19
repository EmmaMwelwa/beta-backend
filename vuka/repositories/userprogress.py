from datetime import date
from typing import List, Set, Tuple, Optional  
from sqlalchemy import func
from sqlalchemy.orm import Session
from vuka.models.userprogress import UserProgress
from vuka.models.verifiedassessment import VerifiedAssessment

class UserProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, progress_id: int) -> Optional[UserProgress]:  
        return self.db.get(UserProgress, progress_id)

    def list(self, skip: int = 0, limit: int = 100) -> List[UserProgress]: 
        return self.db.query(UserProgress).offset(skip).limit(limit).all()

    def create(self, data: dict) -> UserProgress:
        db_obj = UserProgress(**data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: UserProgress, updates: dict) -> UserProgress:
        for key, value in updates.items():
            setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: UserProgress) -> None:
        self.db.delete(db_obj)
        self.db.commit()

    def list_by_user(self, user_id: int) -> List[UserProgress]:  
        return self.db.query(UserProgress).filter(UserProgress.user_id == user_id).all()

    def get_most_recent(self, user_id: int) -> Optional[UserProgress]:  
        return (
            self.db.query(UserProgress)
            .join(VerifiedAssessment, UserProgress.assessment_id == VerifiedAssessment.assessment_id)
            .filter(UserProgress.user_id == user_id)
            .order_by(VerifiedAssessment.assessment_date.desc())
            .first()
        )

    def get_average_score(self, user_id: int) -> int:
        avg = (
            self.db.query(func.avg(UserProgress.score))
            .filter(UserProgress.user_id == user_id)
            .scalar()
        )
        return round(avg) if avg is not None else 0

    def get_average_score_by_category(self, user_id: int) -> List[Tuple[str, int]]: 
        rows = (
            self.db.query(
                VerifiedAssessment.category,
                func.avg(UserProgress.score),
            )
            .join(VerifiedAssessment, UserProgress.assessment_id == VerifiedAssessment.assessment_id)
            .filter(UserProgress.user_id == user_id)
            .group_by(VerifiedAssessment.category)
            .all()
        )
        return [(category, round(avg)) for category, avg in rows]

    def get_active_dates_in_range(self, user_id: int, start: date, end: date) -> Set[date]:  
        rows = (
            self.db.query(VerifiedAssessment.assessment_date)
            .join(UserProgress, UserProgress.assessment_id == VerifiedAssessment.assessment_id)
            .filter(
                UserProgress.user_id == user_id,
                VerifiedAssessment.assessment_date >= start,
                VerifiedAssessment.assessment_date <= end,
            )
            .all()
        )
        return {row[0].date() for row in rows}

    def get_recent_completed(self, user_id: int, limit: int = 5) -> List[Tuple[str, date, int]]: 
        rows = (
            self.db.query(
                VerifiedAssessment.category,
                VerifiedAssessment.assessment_date,
                UserProgress.score,
            )
            .join(VerifiedAssessment, UserProgress.assessment_id == VerifiedAssessment.assessment_id)
            .filter(UserProgress.user_id == user_id)
            .order_by(VerifiedAssessment.assessment_date.desc())
            .limit(limit)
            .all()
        )
        return [(category, assessment_date.date(), score) for category, assessment_date, score in rows]