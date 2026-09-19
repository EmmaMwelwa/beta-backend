from typing import Optional, Sequence
from sqlalchemy.orm import Session
from vuka.models.contents import Content


class ContentRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = Content

    def get_by_id(self, content_id: int):
        return self.db.get(self.model, content_id)


    def get_by_url(self, external_media_url: str):
        return (
            self.db.query(self.model)
            .filter(self.model.external_media_url == external_media_url)
            .first()
    )

    def get_all(self, skip: int = 0, limit: int = 50):
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, data: dict) -> Content:
        db_record = self.model(**data)
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(self, content_id: int, data: dict):
        db_record = self.get_by_id(content_id)
        if db_record:
            for key, value in data.items():
                setattr(db_record, key, value)
            self.db.commit()
            self.db.refresh(db_record)
        return db_record

    def delete(self, content_id: int) -> bool:
        db_record = self.get_by_id(content_id)
        if db_record:
            self.db.delete(db_record)
            self.db.commit()
            return True
        return False