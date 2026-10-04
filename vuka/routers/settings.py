from fastapi import APIRouter, BackgroundTasks, Depends, status

from vuka.dependency import get_current_user
from vuka.models.registration import Registration
from vuka.schemas.settings import SupportTicketCreate, SupportTicketResponse
from vuka.services.settings import create_support_request


router = APIRouter(prefix="/support", tags=["Support"])


@router.post(
    "/tickets",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    payload: SupportTicketCreate,
    background_tasks: BackgroundTasks,
    current_user: Registration = Depends(get_current_user),
):
    return create_support_request(
        user=current_user,
        category=payload.category.value,
        message=payload.message,
        background_tasks=background_tasks,
    )