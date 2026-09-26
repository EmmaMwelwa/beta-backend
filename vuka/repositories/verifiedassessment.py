from sqlalchemy.orm import Session
from vuka.models.verifiedassessment import VerifiedAssessment


class VerifiedAssessmentRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = VerifiedAssessment

    def create(
        self,
        user_id: int,
        generated_assessment_id: int,
        category: str,
        score: int = 0
    ):
        assessment = self.model(
            user_id=user_id,
            generated_assessment_id=generated_assessment_id,
            category=category,
            score=score,
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get_by_id(self, assessment_id: int):
        return self.db.query(self.model).filter(
            self.model.assessment_id == assessment_id
        ).first()

    def get(self, assessment_id: int):
        return self.get_by_id(assessment_id)

    def get_all(self):
        return self.db.query(self.model).all()
    
    def update(self, assessment_id: int, assessment_update: VerifiedAssessment):
        db_assessment = self.get_by_id(assessment_id)
        if not db_assessment:
            return None

        if hasattr(assessment_update, "model_dump"):
            update_data = assessment_update.model_dump(exclude_unset=True)
        else:
            update_data = assessment_update

        for key, value in update_data.items():
            setattr(db_assessment, key, value)

        self.db.commit()
        self.db.refresh(db_assessment)
        return db_assessment

    def delete(self, assessment_id: int):
        assessment = self.get_by_id(assessment_id)
        if assessment:
            self.db.delete(assessment)
            self.db.commit()
        return assessment