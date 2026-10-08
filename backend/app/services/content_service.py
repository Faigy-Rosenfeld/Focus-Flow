from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.video import Video
from app.schemas.video import VideoCreate, VideoUpdate


def list_videos(db: Session) -> list[Video]:
    return list(db.scalars(select(Video).order_by(Video.added_date.desc())).all())


def get_video(db: Session, video_id: int) -> Video:
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return video


def get_video_by_youtube_id(db: Session, youtube_id: str) -> Video | None:
    return db.scalar(select(Video).where(Video.youtube_id == youtube_id))


def create_video(db: Session, payload: VideoCreate, user: User) -> Video:
    existing = get_video_by_youtube_id(db, payload.youtube_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="YouTube id already exists")

    video = Video(
        youtube_id=payload.youtube_id.strip(),
        name=payload.name.strip(),
        description=payload.description.strip(),
        subject_name=payload.subject_name.strip() or "general",
        length_seconds=payload.length_seconds,
        upload_by=user.user_id,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def update_video(db: Session, video_id: int, payload: VideoUpdate, user: User) -> Video:
    video = get_video(db, video_id)
    if video.upload_by is not None and video.upload_by != user.user_id and user.permission < 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this video")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(video, key, value)
    db.commit()
    db.refresh(video)
    return video


def delete_video(db: Session, video_id: int, user: User) -> None:
    video = get_video(db, video_id)
    if video.upload_by is not None and video.upload_by != user.user_id and user.permission < 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this video")
    db.delete(video)
    db.commit()
