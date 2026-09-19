from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from vuka.dependency import get_current_user
from vuka.models.registration import Registration
from vuka.schemas.onboarding import OnboardingCreate, OnboardingUpdate, OnboardingResponse
from vuka.services.onboarding import (create_onboarding, get_my_onboarding, get_onboardings, get_onboarding, update_onboarding, delete_onboarding,
)

router = APIRouter(tags=["Onboarding"])

@router.post("/", response_model=OnboardingResponse)
def create(
    onboarding: OnboardingCreate,
    db: Session = Depends(get_db),
    current_user: Registration = Depends(get_current_user),
):
    return create_onboarding(db, onboarding, current_user.user_id)

@router.get("/me", response_model=OnboardingResponse)
def get_my(
    db: Session = Depends(get_db),
    current_user: Registration = Depends(get_current_user),
):
    return get_my_onboarding(db, current_user.user_id)

@router.get("/", response_model=list[OnboardingResponse])
def get_all(db: Session = Depends(get_db)):
    return get_onboardings(db)

@router.get("/{onboarding_id}", response_model=OnboardingResponse)
def get_one(
    onboarding_id: int,
    db: Session = Depends(get_db),
):
    return get_onboarding(db, onboarding_id)

@router.patch("/{onboarding_id}", response_model=OnboardingResponse)
def update(
    onboarding_id: int,
    onboarding: OnboardingUpdate,
    db: Session = Depends(get_db),
):
    return update_onboarding(db, onboarding_id, onboarding)

@router.delete("/{onboarding_id}")
def delete(
    onboarding_id: int,
    db: Session = Depends(get_db),
):
    return delete_onboarding(db, onboarding_id)