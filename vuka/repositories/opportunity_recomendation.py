from __future__ import annotations
from sqlalchemy.orm import Session

from vuka.models.opportunity_recommendation import OpportunityRecommendation
from vuka.schemas.opportunity_recommendation import (
    OpportunityRecommendationCreate,
    OpportunityRecommendationUpdate,
)


class OpportunityRecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, opportunity_id: int) -> OpportunityRecommendation | None:
        return (
            self.db.query(OpportunityRecommendation)
            .filter(OpportunityRecommendation.opportunity_id == opportunity_id)
            .first()
        )

    def list(self, skip: int = 0, limit: int = 100) -> list[OpportunityRecommendation]:
        return self.db.query(OpportunityRecommendation).offset(skip).limit(limit).all()

    def list_by_user(self, user_id: int) -> list[OpportunityRecommendation]:
        return (
            self.db.query(OpportunityRecommendation)
            .filter(OpportunityRecommendation.user_id == user_id)
            .all()
        )

    def list_urls_for_user(self, user_id: int) -> set[str]:
        rows = (
            self.db.query(OpportunityRecommendation.external_media_url)
            .filter(OpportunityRecommendation.user_id == user_id)
            .all()
        )
        return {row[0] for row in rows}

    def list_urls_by_subject(self, subject_field) -> set[str]:
        rows = (
            self.db.query(OpportunityRecommendation.external_media_url)
            .filter(OpportunityRecommendation.subject_field == subject_field)
            .all()
        )
        return {row[0] for row in rows}

    def list_by_subject(self, subject_field, skip: int = 0, limit: int = 100) -> list[OpportunityRecommendation]:
        return (
            self.db.query(OpportunityRecommendation)
            .filter(OpportunityRecommendation.subject_field == subject_field)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_unassigned(self, skip: int = 0, limit: int = 100) -> list[OpportunityRecommendation]:
        return (
            self.db.query(OpportunityRecommendation)
            .filter(OpportunityRecommendation.user_id.is_(None))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, data: OpportunityRecommendationCreate) -> OpportunityRecommendation:
        record = OpportunityRecommendation(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(
        self, record: OpportunityRecommendation, data: OpportunityRecommendationUpdate
    ) -> OpportunityRecommendation:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: OpportunityRecommendation) -> None:
        self.db.delete(record)
        self.db.commit()