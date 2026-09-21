from fastapi import APIRouter, Depends, status
from vuka.schemas.content_pathway import ContentPathwayCreate, ContentPathwayUpdate, ContentPathwayResponse
from vuka.services.content_pathway import ContentPathwayService
from database import get_db

router = APIRouter(prefix="/content_pathway", tags=["Content Pathways"])

def get_pathway_service(db=Depends(get_db)):
    return ContentPathwayService(db)

@router.post("", response_model=ContentPathwayResponse, status_code=status.HTTP_201_CREATED)
def create_pathway(pathway_in: ContentPathwayCreate, service: ContentPathwayService = Depends(get_pathway_service)):
    return service.generate_pathway(pathway_in)


@router.get("/user/{user_id}", response_model=list[ContentPathwayResponse])
def get_user_pathways(
    user_id: int,
    service: ContentPathwayService = Depends(get_pathway_service),
):
    return service.get_user_guided_pathways(user_id)

@router.get("/{content_pathway_id}", response_model=ContentPathwayResponse)
def get_pathway(content_pathway_id: int, service: ContentPathwayService = Depends(get_pathway_service)):
    return service.retrieve_pathway(content_pathway_id)

@router.patch("/{content_pathway_id}", response_model=ContentPathwayResponse)
def update_pathway(content_pathway_id: int, payload: ContentPathwayUpdate, service: ContentPathwayService = Depends(get_pathway_service)):
    return service.modify_pathway(content_pathway_id, payload)

@router.delete("/{content_pathway_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pathway(content_pathway_id: int, service: ContentPathwayService = Depends(get_pathway_service)):
    service.remove_pathway(content_pathway_id)
    return None