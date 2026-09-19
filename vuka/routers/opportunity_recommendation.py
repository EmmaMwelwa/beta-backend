from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from vuka.dependency import get_current_user, require_admin
from vuka.models.registration import Registration
from vuka.models.enums import SubjectFieldEnum

from vuka.schemas.opportunity_recommendation import (
    OpportunityRecommendationCreate,
    OpportunityRecommendationRead,
    OpportunityRecommendationUpdate,
    OpportunitySubjectFetchRequest,
)
from vuka.services.opportunity_recommendation import (
    OpportunityRecommendationService,
)
router = APIRouter(
    prefix="/opportunity-recommendations",
    tags=["Opportunity Recommendations"],
)
@router.post(
    "/",
    response_model=OpportunityRecommendationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_opportunity(
    data: OpportunityRecommendationCreate,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    return OpportunityRecommendationService(db).create_opportunity(data)

@router.get(
    "/",
    response_model=list[OpportunityRecommendationRead],
)
def list_opportunities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    return OpportunityRecommendationService(
        db
    ).list_opportunities(skip, limit)

@router.get(
    "/unassigned",
    response_model=list[OpportunityRecommendationRead],
)
def list_unassigned_opportunities(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    return OpportunityRecommendationService(
        db
    ).list_unassigned_opportunities(skip, limit)

@router.get(
    "/subject/{subject_field}",
    response_model=list[OpportunityRecommendationRead],
)
def list_opportunities_by_subject(
    subject_field: SubjectFieldEnum,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    return OpportunityRecommendationService(
        db
    ).list_opportunities_by_subject(
        subject_field,
        skip,
        limit,
    )

@router.get(
    "/user/{user_id}",
    response_model=list[OpportunityRecommendationRead],
)
def list_opportunities_for_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(get_current_user),
):

    return OpportunityRecommendationService(
        db
    ).list_opportunities_for_user(user_id)

@router.get(
    "/{opportunity_id}",
    response_model=OpportunityRecommendationRead,
)
def get_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    return OpportunityRecommendationService(
        db
    ).get_opportunity(opportunity_id)

@router.patch(
    "/{opportunity_id}",
    response_model=OpportunityRecommendationRead,
)
def update_opportunity(
    opportunity_id: int,
    data: OpportunityRecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    return OpportunityRecommendationService(
        db
    ).patch_opportunity(
        opportunity_id,
        data,
    )

@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    OpportunityRecommendationService(
        db
    ).delete_opportunity(opportunity_id)

@router.post(
    "/fetch-by-subject",
    response_model=list[OpportunityRecommendationRead],
    status_code=status.HTTP_201_CREATED,
    summary="Fetch opportunities for one subject field via Serper",
)
def fetch_opportunities_by_subject(
    payload: OpportunitySubjectFetchRequest,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    service = OpportunityRecommendationService(db)

    return service.fetch_and_store_by_subject(
        payload.subject_field,
        payload.query,
        payload.num_results,
    )

@router.post(
    "/fetch-all-subjects",
    response_model=list[OpportunityRecommendationRead],
    status_code=status.HTTP_201_CREATED,
    summary="Fetch opportunities across every subject field via Serper",
)
def fetch_opportunities_all_subjects(
    num_results: int = 10,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    return OpportunityRecommendationService(
        db
    ).fetch_and_store_all_subjects(num_results)