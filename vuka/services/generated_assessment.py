from __future__ import annotations

import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from vuka.integrations.gemini_client import GeminiClient
from vuka.models.enums import CategoryEnum
from vuka.repositories.contents import ContentRepository
from vuka.repositories.generated_assessment import GeneratedAssessmentRepository



class GeneratedAssessmentService:
    def __init__(self, db: Session,gemini_client: GeminiClient | None = None):
        self.content_repo = ContentRepository(db)
        self.repo = GeneratedAssessmentRepository(db)

        self._gemini_client = (gemini_client or GeminiClient())
        

    @property
    def gemini_client(self):
        return self._gemini_client



    def get_by_content_id(self, content_id: int):
        record = self.repo.get_by_content_id(content_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No generated assessment for content_id={content_id}",
            )
        return record

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip=skip, limit=limit)

    def delete(self, content_id: int):
        deleted = self.repo.delete(content_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No generated assessment for content_id={content_id}",
            )
        return {"message": "Generated assessment deleted successfully"}

    def generate_for_content(self, content_id: int, num_questions: int = 4, category: CategoryEnum | None = None):
        content = self.content_repo.get_by_id(content_id)
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content record not found")

        try:
            quiz = self.gemini_client.generate_quiz(
                media_description=content.media_description,
                source_platform=content.source_platform,
                external_media_url=content.external_media_url,
                num_questions=num_questions,
                category_hint=category.value if category else None,
            )
        except RuntimeError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gemini API communication failure: {e}",
            )

        resolved_category = quiz.get("category", CategoryEnum.CAREER_READINESS.value)
        if resolved_category not in {c.value for c in CategoryEnum}:
            resolved_category = CategoryEnum.CAREER_READINESS.value

        if not quiz:
            raise RuntimeError("Gemini returned an empty response")

        questions = quiz.get("questions", [])

        if len(questions) == 0:
            raise RuntimeError("No assessment questions were generated")


        record = self.repo.upsert(
            content_id=content_id,
            category=resolved_category,
            questions_json=json.dumps(questions),
            model_used=self.gemini_client.model,
        )

        
        return record



    def generate_for_all(self,num_questions: int = 4,skip_existing: bool = True):

        contents = self.content_repo.get_all(skip=0,limit=10000)

        generated = []
        skipped = []
        failed = []


        for content in contents:

            if skip_existing and self.repo.get_by_content_id(content.content_id):
                skipped.append(content.content_id)
                continue


        try:
            record = self.generate_for_content(
                content.content_id,
                num_questions=num_questions
            )

            generated.append(record)


        except Exception as e:
            failed.append({
                "content_id": content.content_id,
                "error": str(e)
            })


        if len(generated) == 0 and len(failed) > 0:
            raise HTTPException(
                status_code=502,
                detail={
                    "message":"Gemini failed to generate assessments",
                    "failed":failed
                }
            )


        return {
            "generated": generated,
            "skipped_existing": skipped,
            "failed": [],
            "message": "Assessments generated successfully"
        }