from __future__ import annotations
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from vuka.integrations.serper_client import SerperClient
from vuka.models.enums import SubjectFieldEnum
from vuka.models.registration import Registration
from vuka.repositories.opportunity_recomendation import OpportunityRecommendationRepository
from vuka.schemas.opportunity_recommendation import (
    OpportunityRecommendationCreate,
    OpportunityRecommendationUpdate,
)

DEFAULT_SUBJECT_QUERIES: dict[SubjectFieldEnum, str] = {
    SubjectFieldEnum.TECH: "tech scholarships and internships for high school graduates in Kenya",
    SubjectFieldEnum.FINTECH: "fintech scholarships and internships for young people in Kenya",
    SubjectFieldEnum.ENGINEERING: "engineering scholarships and internships for high school graduates in Kenya",
    SubjectFieldEnum.BUSINESS: "business and entrepreneurship scholarships for youth in Kenya",
    SubjectFieldEnum.HEALTHCARE: "healthcare and medical scholarships for high school graduates in Kenya",
    SubjectFieldEnum.CREATIVE_ARTS: "creative arts and design scholarships for youth in Kenya",
    SubjectFieldEnum.OTHER: "scholarships and opportunities for high school graduates in Kenya",
}


class OpportunityRecommendationService:
    def __init__(self, db: Session, serper_client: SerperClient | None = None):
        self.db = db
        self.repository = OpportunityRecommendationRepository(db)
        self._serper_client = serper_client


    def get_opportunity(self, opportunity_id: int):
        record = self.repository.get(opportunity_id)
        if not record:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
        return record

    def list_opportunities(self, skip: int = 0, limit: int = 100):
        return self.repository.list(skip, limit)

    def list_opportunities_for_user(self, user_id: int):
        return self.repository.list_by_user(user_id)

    def list_opportunities_by_subject(self, subject_field: SubjectFieldEnum, skip: int = 0, limit: int = 100):
        return self.repository.list_by_subject(subject_field, skip, limit)

    def list_unassigned_opportunities(self, skip: int = 0, limit: int = 100):
        return self.repository.list_unassigned(skip, limit)

    def _user_exists(self, user_id: int) -> bool:
        if user_id is None:
            return False
        return self.db.query(Registration).filter(Registration.user_id == user_id).first() is not None

    def create_opportunity(self, data: OpportunityRecommendationCreate):
        if data.user_id is not None and not self._user_exists(data.user_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return self.repository.create(data)

    def patch_opportunity(self, opportunity_id: int, data: OpportunityRecommendationUpdate):
        opportunity = self.get_opportunity(opportunity_id)
        if not opportunity:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
        if data.user_id is not None and not self._user_exists(data.user_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return self.repository.update(opportunity, data)
    
    def delete_opportunity(self, opportunity_id: int) -> None:
        record = self.get_opportunity(opportunity_id)
        self.repository.delete(record)

    def fetch_and_store_by_subject(
        self,
        subject_field: SubjectFieldEnum,
        query: str | None = None,
        num_results: int = 10,
    ) -> list:
        search_query = query or DEFAULT_SUBJECT_QUERIES[subject_field]

        client = self._serper_client or SerperClient()
        results = client.search(search_query, num_results)

        already_stored = self.repository.list_urls_by_subject(subject_field)
        created = []

        for result in results:
            link = result.get("link")
            if not link or link in already_stored:
                continue

            data = OpportunityRecommendationCreate(
                user_id=None,
                subject_field=subject_field,
                external_media_url=link,
                source_platform=urlparse(link).netloc or "unknown",
                media_description=result.get("snippet") or result.get("title", ""),
                opportunity_date=datetime.now(timezone.utc),
            )
            created.append(self.repository.create(data))
            already_stored.add(link)

        return created

    def fetch_and_store_all_subjects(self, num_results: int = 10) -> list:
        created = []
        for subject_field in SubjectFieldEnum:
            created.extend(self.fetch_and_store_by_subject(subject_field, None, num_results))
        return created