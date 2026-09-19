from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from vuka.dependency import get_current_user, require_admin
from vuka.models.registration import Registration
from vuka.services.userprogress import UserProgressService
from vuka.schemas.verifiedassessment import AssessmentSubmission
from vuka.schemas.userprogress import (
    UserProgressCreate,
    UserProgressResponse,
    ProgressSummary,
)

router = APIRouter(prefix="/user-progress", tags=["User Progress"])


def get_user_progress_service(db: Session = Depends(get_db)):
    return UserProgressService(db)

@router.post("/", response_model=UserProgressResponse, status_code=201)
def create_progress(
    progress: UserProgressCreate,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(get_current_user),
):
    if progress.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create progress for another user",
        )
    service = get_user_progress_service(db)
    return service.create(progress)

@router.get("/", response_model=list[UserProgressResponse])
def get_all_progress_records(
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    service = get_user_progress_service(db)
    return service.get_all()

@router.get("/summary/{user_id}", response_model=ProgressSummary)
def get_user_dashboard_summary(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(get_current_user),
):
    if current_user.user_type != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another user's progress",
        )
    service = get_user_progress_service(db)
    return service.get_summary(user_id)

@router.get("/{progress_id}", response_model=UserProgressResponse)
def get_one_progress_record(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(get_current_user),
):
    service = get_user_progress_service(db)
    progress = service.get(progress_id)
    if (
        current_user.user_type != "admin"
        and progress.user_id != current_user.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another user's progress",
        )
    return progress

@router.patch("/{progress_id}/submit", response_model=UserProgressResponse)
def submit_assessment_for_evaluation(
    progress_id: int,
    submission: AssessmentSubmission,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(get_current_user),
):
    service = get_user_progress_service(db)

    progress = service.get(progress_id)

    if (
        current_user.user_type != "admin"
        and progress.user_id != current_user.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot modify another user's progress",
        )

    return service.evaluate_mock_and_process(
        progress_id,
        submission,
    )
@router.delete("/{progress_id}")
def delete(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(require_admin),
):
    service = get_user_progress_service(db)
    service.delete(progress_id)
    return {"message": "Progress deleted successfully"}