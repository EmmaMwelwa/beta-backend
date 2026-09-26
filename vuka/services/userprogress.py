from datetime import date, datetime, timedelta, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from vuka.models.userprogress import UserProgress
from vuka.repositories.userprogress import UserProgressRepository
from vuka.repositories.verifiedassessment import VerifiedAssessmentRepository
from vuka.repositories.generated_assessment import GeneratedAssessmentRepository
from vuka.repositories.registration import RegistrationRepository
from vuka.schemas.userprogress import (
    UserProgressCreate,
    UserProgressUpdate,
    ProgressSummary,
    CategoryScore,
    CompletedAssessment,
    WeeklyActivityDay,
)
import json

from vuka.repositories.generated_assessment import GeneratedAssessmentRepository

WEEKDAY_LABELS = ["M", "T", "W", "T", "F", "S", "S"]


class UserProgressService:

    def __init__(self, db: Session):
        self.repo = UserProgressRepository(db)
        self.registration_repo = RegistrationRepository(db)
        self.assessment_repo = VerifiedAssessmentRepository(db)
        self.generated_assessment_repo = GeneratedAssessmentRepository(db)

    def _build_performance_payload(self, calculated_score: int) -> dict:
        if 75 <= calculated_score <= 100:
            return {
                "performance_tier": "High",
                "description": "Exceptional mastery of skills learnt.",
                "what_happens_next": "Unlocks unlimited opportunities",
                "can_retake": False,
            }

        if 50 <= calculated_score <= 74:
            return {
                "performance_tier": "Average",
                "description": "Satisfactory, grasps the core concepts and meets the basic standards.",
                "what_happens_next": "Unlocks limited opportunities",
                "can_retake": False,
            }

        return {
            "performance_tier": "Low",
            "description": "Unsatisfactory, missed core concepts and need for intervention.",
            "what_happens_next": (
                "Does not unlock opportunities. "
                "Given chances to retake assessments."
            ),
            "can_retake": True,
        }

    def _compute_streak(self, user_id: int, activity_date: date) -> int:
        last_record = self.repo.get_most_recent(user_id)

        if not last_record:
            return 1

        last_date = last_record.assessment.assessment_date.date()

        gap_days = (activity_date - last_date).days

        if gap_days <= 0:
            return last_record.streak_count

        if gap_days == 1:
            return last_record.streak_count + 1

        return 1

    def create(self, payload: UserProgressCreate) -> UserProgress:
        if not self.registration_repo.get_registration(payload.user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        generated_assessment = self.generated_assessment_repo.get_by_id(
            payload.assessment_id
        )

        if not generated_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated assessment not found",
            )

        verified_assessment = (
            self.assessment_repo.get_by_user_and_generated_assessment(
                user_id=payload.user_id,
                generated_assessment_id=generated_assessment.generated_assessment_id,
            )
        )

        if not verified_assessment:
            verified_assessment = self.assessment_repo.create(
                user_id=payload.user_id,
                generated_assessment_id=generated_assessment.generated_assessment_id,
                category=generated_assessment.category,
                score=0,
            )
        streak_count = self._compute_streak(
            payload.user_id,
            verified_assessment.assessment_date.date(),
        )

        data = {
            "user_id": payload.user_id,
            "assessment_id": verified_assessment.assessment_id,
            "score": 0,
            "streak_count": streak_count,
        }
        return self.repo.create(data)
    
    def get(self, progress_id: int) -> UserProgress:
        db_obj = self.repo.get(progress_id)

        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress record not found",
            )

        return db_obj

    def get_by_id(self, progress_id: int) -> UserProgress:
        return self.get(progress_id)

    def get_all(self) -> List[UserProgress]:
        return self.list()


    def evaluate_mock_and_process(self,progress_id: int,submission,) -> UserProgress:

        progress = self.get(progress_id)

        verified_assessment = self.assessment_repo.get(
            progress.assessment_id
        )
        
        if not verified_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verified assessment not found",
            )

        if progress.assessment_id != verified_assessment.assessment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment does not match this progress record",
            )

        generated_assessment = (
            self.generated_assessment_repo.get_by_id(
                verified_assessment.generated_assessment_id
            )
        )

        if not generated_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generated assessment not found",
            )

        questions = json.loads(generated_assessment.questions)

        answers_by_index = {
            answer["question_index"]: answer["selected_index"]
            for answer in submission.answers
        }

        correct_count = 0

        for index, question in enumerate(questions):
            selected_index = answers_by_index.get(index)

            if selected_index == question["correct_index"]:
                correct_count += 1

        total_questions = len(questions)

        score = (
            round((correct_count / total_questions) * 100)
            if total_questions
            else 0
        )

        verified_assessment_update = {
            "score": score,
        }

        self.assessment_repo.update(
            verified_assessment.assessment_id,
            verified_assessment_update,
        )

        updated_data = {
            "score": score,
        }

        return self.repo.update(progress, updated_data,)
    
    def list(self, skip: int = 0, limit: int = 100,) -> List[UserProgress]:
        return self.repo.list(skip, limit)
    
    def list_by_user(self, user_id: int,) -> List[UserProgress]:
        return self.repo.list_by_user(user_id)

    def update(self, progress_id: int, payload: UserProgressUpdate,) -> UserProgress:
        db_obj = self.get(progress_id)
        updates = payload.model_dump(
            exclude_unset=True)

        return self.repo.update(
            db_obj,
            updates,
        )

    def delete(self, progress_id: int,) -> None:
        db_obj = self.get(progress_id)
        self.repo.delete(db_obj)

    def get_summary(
        self,
        user_id: int,
    ) -> ProgressSummary:

        if not self.registration_repo.get_registration(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        today = datetime.now(timezone.utc).date()

        week_start = today - timedelta(
            days=today.weekday()
        )

        week_end = week_start + timedelta(days=6)

        active_dates = self.repo.get_active_dates_in_range(
            user_id,
            week_start,
            week_end,
        )

        weekly_activity = [
            WeeklyActivityDay(
                weekday=WEEKDAY_LABELS[i],
                date=week_start + timedelta(days=i),
                completed=(
                    week_start + timedelta(days=i)
                ) in active_dates,
            )
            for i in range(7)
        ]

        most_recent = self.repo.get_most_recent(
            user_id
        )

        current_streak = (
            most_recent.streak_count
            if most_recent
            else 0
        )

        return ProgressSummary(
            overall_progress=self.repo.get_average_score(
                user_id
            ),

            category_breakdown=[
                CategoryScore(
                    category=category,
                    average_score=avg,
                )
                for category, avg in self.repo.get_average_score_by_category(
                    user_id
                )
            ],

            current_streak=current_streak,

            weekly_activity=weekly_activity,

            completed_assessments=[
                CompletedAssessment(
                    category=category,
                    assessment_date=d,
                    score=score,
                )
                for category, d, score in self.repo.get_recent_completed(
                    user_id,
                    limit=5,
                )
            ],
        )