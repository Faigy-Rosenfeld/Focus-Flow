from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.video import VideoCreate, VideoPublic, VideoUpdate
from app.services import content_service

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/videos", response_model=list[VideoPublic])
def list_videos(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[VideoPublic]:
    return [VideoPublic.model_validate(v) for v in content_service.list_videos(db)]


@router.get("/videos/{video_id}", response_model=VideoPublic)
def get_video(
    video_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> VideoPublic:
    return VideoPublic.model_validate(content_service.get_video(db, video_id))


@router.post("/videos", response_model=VideoPublic, status_code=status.HTTP_201_CREATED)
def create_video(
    payload: VideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoPublic:
    return VideoPublic.model_validate(content_service.create_video(db, payload, current_user))


@router.patch("/videos/{video_id}", response_model=VideoPublic)
def update_video(
    video_id: int,
    payload: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VideoPublic:
    return VideoPublic.model_validate(content_service.update_video(db, video_id, payload, current_user))


@router.delete("/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    content_service.delete_video(db, video_id, current_user)
