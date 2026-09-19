import asyncio
from typing import Any, Awaitable
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from vuka.integrations.serper_client import SerperClient
from vuka.integrations.trivia_client import OpenTriviaClient
from vuka.integrations.youtube_client import YouTubeClient
from vuka.schemas.contents import ContentResponse, ContentUpdate, PipelineQuerySchema, PipelineResponseSchema
from vuka.services.contents import ContentService

router = APIRouter(tags=["Contents"])

def get_service(db: Session = Depends(get_db)) -> ContentService:
    return ContentService(db)

@router.post("/serper", response_model=list[ContentResponse], status_code=status.HTTP_201_CREATED)
def fetch_and_save_serper(query: str, service: ContentService = Depends(get_service)):
    return service.fetch_and_save_from_serper(query)

@router.post("/youtube", response_model=list[ContentResponse], status_code=status.HTTP_201_CREATED)
def fetch_and_save_youtube(query: str, service: ContentService = Depends(get_service)):
    return service.fetch_and_save_from_youtube(query)

@router.post("/generate-pipeline-data", response_model=PipelineResponseSchema, status_code=status.HTTP_200_OK, summary="Generate social, educational, and opportunity data")
async def generate_pipeline_data(payload: PipelineQuerySchema) -> PipelineResponseSchema:
    """Run all external content pipelines concurrently and return one response."""
    serper_client = SerperClient()
    youtube_client = YouTubeClient()
    trivia_client = OpenTriviaClient()
    tasks: list[tuple[str, Awaitable[Any]]] = []
    for platform in payload.platforms:
        if platform == "youtube":
            tasks.append(("youtube", youtube_client.search(keyword=payload.keyword, max_results=payload.max_results)))
        else:
            tasks.append((platform, serper_client.search_social(platform=platform, keyword=payload.keyword, num_results=payload.max_results)))
    tasks.append(("education", trivia_client.fetch_questions(amount=payload.max_results, category=payload.quiz_category, difficulty=payload.quiz_difficulty)))
    tasks.append(("opportunities", serper_client.search_opportunities(keyword=payload.keyword, num_results=payload.max_results)))
    results = await asyncio.gather(*(task for _, task in tasks), return_exceptions=True)
    social: dict[str, list[dict[str, str]]] = {}
    education: list[dict[str, Any]] = []
    opportunities: list[dict[str, str]] = []
    errors: list[str] = []
    failed_tasks = 0
    for (name, _), result in zip(tasks, results):
        if isinstance(result, Exception):
            failed_tasks += 1
            errors.append(f"{name}: {result}")
            continue
        if name == "education":
            education = result
        elif name == "opportunities":
            opportunities = result
        else:
            social[name] = result
    if failed_tasks == len(tasks):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail={"message": "All external pipeline services failed.", "errors": errors})
    return PipelineResponseSchema(
        keyword=payload.keyword,
        social=social,
        education={"category": payload.quiz_category, "difficulty": payload.quiz_difficulty, "questions": education},
        opportunities=opportunities,
        errors=errors,
    )

@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int, service: ContentService = Depends(get_service)):
    return service.get_by_id(content_id)

@router.get("", response_model=list[ContentResponse])
def list_contents(skip: int = 0, limit: int = 50, service: ContentService = Depends(get_service)):
    return service.get_all(skip, limit)

@router.put("/{content_id}", response_model=ContentResponse)
def update_content(content_id: int, payload: ContentUpdate, service: ContentService = Depends(get_service)):
    return service.update(content_id, payload)

@router.delete("/{content_id}", status_code=status.HTTP_200_OK)
def delete_content(content_id: int, service: ContentService = Depends(get_service)):
    service.delete(content_id)
    return {"message": "Content deleted successfully"}
