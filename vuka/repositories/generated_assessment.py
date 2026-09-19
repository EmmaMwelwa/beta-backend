from sqlalchemy.orm import Session
from vuka.models.generated_assessment import GeneratedAssessment


class GeneratedAssessmentRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = GeneratedAssessment

    def get_by_content_id(self, content_id: int):
        return (
            self.db.query(self.model)
            .filter(self.model.content_id == content_id)
            .first()
        )

    def get_by_id(self, generated_assessment_id: int):
        return self.db.get(self.model, generated_assessment_id)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def upsert(self, content_id: int, category: str, questions_json: str, model_used: str):
        existing = self.get_by_content_id(content_id)
        if existing:
            existing.category = category
            existing.questions = questions_json
            existing.model_used = model_used
            self.db.commit()
            self.db.refresh(existing)
            return existing

        record = self.model(
            content_id=content_id,
            category=category,
            questions=questions_json,
            model_used=model_used,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, content_id: int) -> bool:
        existing = self.get_by_content_id(content_id)
        if existing:
            self.db.delete(existing)
            self.db.commit()
            return True
        return False
