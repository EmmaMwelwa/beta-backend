from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from vuka.services.verifiedassessment import VerifiedAssessmentService

from vuka.schemas.verifiedassessment import (
    VerifiedAssessmentCreate,
    VerifiedAssessmentUpdate,
    VerifiedAssessmentResponse,
    AssessmentSubmission,
)

router = APIRouter(prefix="/verified-assessment", tags=["Verified Assessment"])


def get_verified_assessment_service(db: Session) -> VerifiedAssessmentService:
    return VerifiedAssessmentService(db)


@router.post("/", response_model=VerifiedAssessmentResponse)
def create_assessment(assessment: VerifiedAssessmentCreate, db: Session = Depends(get_db)):
    service = get_verified_assessment_service(db)
    return service.create(assessment)


@router.get("/", response_model=list[VerifiedAssessmentResponse])
def get_all(db: Session = Depends(get_db)):
    service = get_verified_assessment_service(db)
    return service.get_all()


@router.get("/{assessment_id}", response_model=VerifiedAssessmentResponse)
def get_one(assessment_id: int, db: Session = Depends(get_db)):
    service = get_verified_assessment_service(db)
    assessment = service.get_by_id(assessment_id)
    return assessment


@router.patch("/{assessment_id}", response_model=VerifiedAssessmentResponse)
def update_assessment(assessment_id: int, assessment_update: VerifiedAssessmentUpdate, db: Session = Depends(get_db)):
    service = get_verified_assessment_service(db)
    assessment = service.update(assessment_id, assessment_update)
    return assessment


@router.delete("/{assessment_id}")
def delete(assessment_id: int, db: Session = Depends(get_db)):
    service = get_verified_assessment_service(db)
    assessment = service.delete(assessment_id)
    return {"message": "Assessment deleted successfully"}