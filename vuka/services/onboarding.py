from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from vuka.repositories.onboarding import OnboardingRepository
from vuka.schemas.onboarding import OnboardingCreate, OnboardingUpdate

def create_onboarding(db: Session, onboarding: OnboardingCreate, user_id: int):
    repo = OnboardingRepository(db)

    if repo.get_by_user(user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Onboarding assessment already exists for this user",
        )

    data = onboarding.model_dump()
    data["user_id"] = user_id
    return repo.create(data)

def get_my_onboarding(db: Session, user_id: int):
    repo = OnboardingRepository(db)
    record = repo.get_by_user(user_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding assessment not found",
        )

    return record

def get_onboardings(db: Session):
    repo = OnboardingRepository(db)
    return db.query(repo.model).all()

def get_onboarding(db: Session, onboarding_id: int):
    repo = OnboardingRepository(db)
    record = repo.get_by_id(onboarding_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding assessment not found",
        )

    return record

def update_onboarding(
    db: Session,
    onboarding_id: int,
    onboarding: OnboardingUpdate,
):
    repo = OnboardingRepository(db)
    existing = repo.get_by_id(onboarding_id)

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding assessment not found",
        )

    updates = onboarding.model_dump(exclude_unset=True)
    return repo.update(onboarding_id, updates)

def delete_onboarding(db: Session, onboarding_id: int):
    repo = OnboardingRepository(db)

    if not repo.get_by_id(onboarding_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Onboarding assessment not found",
        )

    repo.delete(onboarding_id)
    return {"detail": "Onboarding assessment deleted"}