import os
from datetime import datetime, timezone
from typing import List

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from vuka.models.contents import Content
from vuka.repositories.contents import ContentRepository
from vuka.schemas.contents import ContentCreate, ContentUpdate

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False

load_dotenv()


class ContentService:
    def __init__(self, db: Session):
        self.repo = ContentRepository(db)
        self.serper_api_key = os.getenv("SERPER_API_KEY", "")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")

    def get_by_id(self, content_id: int):
        db_record = self.repo.get_by_id(content_id)
        if not db_record:
            raise HTTPException(status_code=404, detail="Content record not found")
        return db_record

    def get_by_url(self, external_media_url: str):
        return self.repo.get_by_url(external_media_url)

    def get_all(self, skip: int = 0, limit: int = 100):
        return self.repo.get_all(skip=skip, limit=limit)

    def create(self, schema_data: ContentCreate):
        data_dict = schema_data.model_dump()
        data_dict["external_media_url"] = str(data_dict["external_media_url"])
        return self.repo.create(data_dict)

    def update(self, content_id: int, schema_data: ContentUpdate):
        self.get_by_id(content_id)
        data_dict = schema_data.model_dump(exclude_unset=True)
        if "external_media_url" in data_dict and data_dict["external_media_url"]:
            data_dict["external_media_url"] = str(data_dict["external_media_url"])
        return self.repo.update(content_id, data_dict)
       

    def delete(self, content_id: int) -> bool:
        self.get_by_id(content_id)
        return self.repo.delete(content_id)

    def fetch_and_save_from_serper(self, query: str):
        if not self.serper_api_key:
            raise HTTPException(status_code=500, detail="Missing SERPER_API_KEY configuration.")

        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"}
        payload = {"q": query}

        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload, timeout=10.0)
                response.raise_for_status()
                results = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"Serper API communication failure: {str(e)}")

        saved_records = []
        for item in results.get("organic", []):
            media_url = item.get("link")
            if not media_url:
                continue

            content_data = {
                "external_media_url": str(media_url),
                "source_platform": "Serper/Google",
                "media_description": item.get("snippet", "No description provided."),
                "datetime": datetime.now(timezone.utc).replace(tzinfo=None)
            }

            existing = self.repo.get_by_url(content_data["external_media_url"])
            if existing:
                record = self.repo.update(existing.content_id, content_data)
            else:
                record = self.repo.create(content_data)
            saved_records.append(record)

        return saved_records

    def fetch_and_save_from_youtube(self, query: str) -> List[Content]:
        if not self.youtube_api_key:
            raise HTTPException(status_code=500, detail="Missing YOUTUBE_API_KEY configuration.")

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 10,
            "key": self.youtube_api_key
        }

        try:
            with httpx.Client() as client:
                response = client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                results = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"YouTube API communication failure: {str(e)}")

        saved_records = []
        for item in results.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            if not video_id:
                continue

            media_url = f"https://www.youtube.com/watch?v={video_id}"

            pub_time_str = snippet.get("publishedAt")
            if pub_time_str:
                dt_obj = datetime.fromisoformat(pub_time_str.replace("Z", "+00:00")).astimezone(timezone.utc).replace(tzinfo=None)
            else:
                dt_obj = datetime.now(timezone.utc).replace(tzinfo=None)

            content_data = {
                "external_media_url": media_url,
                "source_platform": "YouTube",
                "media_description": snippet.get("description", "No description provided."),
                "datetime": dt_obj
            }

            existing = self.repo.get_by_url(content_data["external_media_url"])
            if existing:
                record = self.repo.update(existing.content_id, content_data)
            else:
                record = self.repo.create(content_data)
            saved_records.append(record)

        return saved_records



