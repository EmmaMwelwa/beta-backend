from sqlalchemy.orm import Session
from vuka.repositories.verifiedassessment import VerifiedAssessmentRepository
from vuka.schemas.verifiedassessment import VerifiedAssessmentCreate, AssessmentProgress, VerifiedAssessmentResponse, AssessmentSubmission, VerifiedAssessmentUpdate

class VerifiedAssessmentService:
    def __init__(self, db: Session):
        self.repository = VerifiedAssessmentRepository(db)

    def create(self, data: VerifiedAssessmentCreate):
        return self.repository.create(user_id=data.user_id, category=data.category, score=0)

    def get_all(self):
        return self.repository.get_all()
        

    def get_by_id(self, assessment_id: int):
        assessment = self.repository.get_by_id(assessment_id)
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="assessment not found")
        return assessment


    def save(self, assessment_id: int, schema: AssessmentProgress):
        assessment = self.get_by_assessment(assessment_id, schema.user_id)  
        if assessment.status == AssessmentProgress.completed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This assessment has already been completed and can no longer be edited.",
            )
        merged_answers = {**assessment.answers, **schema.answers}
        return self.repo.update(
            progress.progress_id,
            {"current_step": schema.current_step, "answers": merged_answers},
        )

    def complete(self, assessment_id: int, user_id: int, final_score : int):
        assessment = self.get_by_id(assessment_id)
        if assessment.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Assessment does not belong to the user.")
        return self.repo.update(progress.progress_id, {"status": ProgressStatus.completed})
        update_data = VerifiedAssessmentUpdate(
            status="completed",
            score=final_score
        )
        return self.repository.update(assessment_id, update_data)

    @staticmethod
    def _assert_owner(progress, user_id: int):
        if progress.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This progress record does not belong to the requesting user.",
            )

    def update(self, assessment_id: int, assessment_update):
        assessment = self.repository.update(assessment_id, assessment_update)
        if not assessment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
        return self.repository.update(assessment_id, assessment_update)

    def delete(self, assessment_id):
        return self.repository.delete(assessment_id)