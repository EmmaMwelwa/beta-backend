from __future__ import annotations
import argparse
from database import SessionLocal
from models.enums import SubjectFieldEnum
from services.opportunity_recommendation import OpportunityRecommendationService


def run(subject: str | None, query: str | None, num_results: int) -> None:
    db = SessionLocal()
    try:
        service = OpportunityRecommendationService(db)

        if subject:
            subject_field = SubjectFieldEnum(subject)
            created = service.fetch_and_store_by_subject(subject_field, query, num_results)
        else:
            created = service.fetch_and_store_all_subjects(num_results)

        print(f"Stored {len(created)} new opportunities.")
        for record in created:
            print(f"  [{record.subject_field.value}] {record.media_description[:70]!r} -> {record.external_media_url}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch opportunities from Serper into the pool table.")
    parser.add_argument(
        choices=[field.value for field in SubjectFieldEnum],
        default=None,
        help="Limit the fetch to one subject field. Omit to run all fields.",
    )
    parser.add_argument("--query", default=None, help="Custom search query (only used with --subject).")
    parser.add_argument("--num-results", type=int, default=10, help="Results per subject field (max 20).")
    args = parser.parse_args()

    run(args.subject, args.query, args.num_results)