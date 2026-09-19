from sqlalchemy.orm import Session
from vuka.models.content_pathway import ContentPathway

class ContentPathwayRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = ContentPathway

    def get_by_id(self, content_pathway_id: int):
        return self.db.get(self.model, content_pathway_id)

    def get_by_content(self, content_id: int):
        return self.db.query(self.model).filter(self.model.content_id == content_id).all()

    def create(self, data: dict):
        db_record = self.model(**data)
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(self, pathway_id: int, data: dict):
        db_record = self.get_by_id(pathway_id)

        if not db_record:
            return None

        for key, value in data.items():
            setattr(db_record, key, value)

        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def delete(self, pathway_id: int) -> bool:
        db_record = self.get_by_id(pathway_id)

        if not db_record:
            return False

        self.db.delete(db_record)
        self.db.commit()
        return True