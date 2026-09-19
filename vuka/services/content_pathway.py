from urllib.parse import urlparse
from fastapi import HTTPException, status
from vuka.models.content_pathway import ContentPathway
from vuka.repositories.content_pathway import ContentPathwayRepository
from vuka.repositories.contents import ContentRepository
from sqlalchemy.orm import Session
from vuka.schemas.content_pathway import ContentPathwayCreate, ContentPathwayUpdate

TRUSTED_MEDIA_DOMAINS = {
    "tiktok.com", "www.tiktok.com",
    "youtube.com", "www.youtube.com",
    "instagram.com", "www.instagram.com",
}

class ContentPathwayService:
    def __init__(self, db: Session):
        self.repo = ContentPathwayRepository(db)

    def generate_pathway(self, schema: ContentPathwayCreate) -> ContentPathway:
        content_repo = ContentRepository(self.repo.db)
        content = content_repo.get_by_id(schema.content_id)

        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found.")

        external_media_url = str(schema.external_media_url)
        self.assert_trusted_url(external_media_url)

        data = {
            "content_id": schema.content_id,
            "external_media_url": external_media_url,
            "media_description": schema.media_description,
            "date": schema.date,
        }
        return self.repo.create(data)

    def retrieve_pathway(self, pathway_id: int):
        pathway = self.repo.get_by_id(pathway_id)

        if not pathway:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content pathway not found.")

        return pathway

    def modify_pathway(self, pathway_id: int, schema: ContentPathwayUpdate):
        self.retrieve_pathway(pathway_id)

        if schema.external_media_url is not None:
            self.assert_trusted_url(str(schema.external_media_url))

        update_data = schema.model_dump(exclude_unset=True, mode="json")

        if "external_media_url" in update_data:
            update_data["external_media_url"] = str(update_data["external_media_url"])

        return self.repo.update(pathway_id, update_data)

    def remove_pathway(self, pathway_id: int):
        self.retrieve_pathway(pathway_id)
        self.repo.delete(pathway_id)

    @staticmethod
    def assert_trusted_url(url: str):
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Only HTTP and HTTPS URLs are allowed.")

        host = parsed.hostname

        if not host:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid media URL.")

        host = host.lower()

        if host not in TRUSTED_MEDIA_DOMAINS:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Media source is not trusted.")