from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from vuka.schemas.generated_assessment import (
    GenerateAllResult,
    GenerateAssessmentRequest,
    GeneratedAssessmentResponse,
)
from vuka.services.generated_assessment import GeneratedAssessmentService

router = APIRouter(prefix="/content-assessments", tags=["Generated Assessments"])


def get_service(db: Session = Depends(get_db)) -> GeneratedAssessmentService:
    return GeneratedAssessmentService(db)


@router.post("/generate/{content_id}", response_model=GeneratedAssessmentResponse)
def generate_assessment(
    content_id: int,
    payload: GenerateAssessmentRequest = GenerateAssessmentRequest(),
    service: GeneratedAssessmentService = Depends(get_service),
):

    return service.generate_for_content(
        content_id, num_questions=payload.num_questions, category=payload.category
    )


@router.post("/generate-all", response_model=GenerateAllResult)
def generate_all(
    num_questions: int = 4,
    skip_existing: bool = True,
    service: GeneratedAssessmentService = Depends(get_service),
):
    return service.generate_for_all(
        num_questions=num_questions,
        skip_existing=skip_existing
    )



@router.get("", response_model=list[GeneratedAssessmentResponse])
def list_generated(skip: int = 0, limit: int = 100, service: GeneratedAssessmentService = Depends(get_service)):
    return service.get_all(skip, limit)


@router.get("/{content_id}", response_model=GeneratedAssessmentResponse)
def get_generated(content_id: int, service: GeneratedAssessmentService = Depends(get_service)):
    return service.get_by_content_id(content_id)


@router.delete("/{content_id}")
def delete_generated(content_id: int, service: GeneratedAssessmentService = Depends(get_service)):
    return service.delete(content_id)