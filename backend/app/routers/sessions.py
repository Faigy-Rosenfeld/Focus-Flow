from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.watch import (
    FocusSampleCreate,
    FocusSampleResponse,
    WatchHistoryItem,
    WatchItemPublic,
    WatchSessionStart,
)
from app.services import watch_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=WatchItemPublic)
def start_session(
    payload: WatchSessionStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WatchItemPublic:
    item = watch_service.start_session(db, current_user, payload)
    return WatchItemPublic.model_validate(item)


@router.get("/history", response_model=list[WatchHistoryItem])
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[WatchHistoryItem]:
    return watch_service.list_history(db, current_user)


@router.post("/{watch_item_id}/focus", response_model=FocusSampleResponse)
def post_focus(
    watch_item_id: int,
    payload: FocusSampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FocusSampleResponse:
    item, score = watch_service.record_focus_sample(db, current_user, watch_item_id, payload)
    return FocusSampleResponse(
        watch_item_id=item.watch_item_id,
        focus_score=score,
        average_focus=item.average_focus or score,
        status=item.status,
    )


@router.post("/{watch_item_id}/end", response_model=WatchItemPublic)
def end_session(
    watch_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WatchItemPublic:
    item = watch_service.end_session(db, current_user, watch_item_id)
    return WatchItemPublic.model_validate(item)
