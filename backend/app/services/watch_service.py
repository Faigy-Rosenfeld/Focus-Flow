from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.video import Video
from app.models.watch import LogData, ModelResult, WatchData, WatchItem
from app.schemas.watch import FocusSampleCreate, WatchHistoryItem, WatchSessionStart
from app.services import content_service


def start_session(db: Session, user: User, payload: WatchSessionStart) -> WatchItem:
    video = content_service.get_video_by_youtube_id(db, payload.youtube_id)
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    active = db.scalar(
        select(WatchItem).where(
            WatchItem.user_id == user.user_id,
            WatchItem.youtube_id == payload.youtube_id,
            WatchItem.status == "active",
        )
    )
    if active:
        return active

    item = WatchItem(user_id=user.user_id, youtube_id=payload.youtube_id, status="active")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_owned_watch_item(db: Session, user: User, watch_item_id: int) -> WatchItem:
    item = db.get(WatchItem, watch_item_id)
    if item is None or item.user_id != user.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watch session not found")
    return item


def record_focus_sample(
    db: Session, user: User, watch_item_id: int, payload: FocusSampleCreate
) -> tuple[WatchItem, float]:
    item = get_owned_watch_item(db, user, watch_item_id)
    if item.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already ended")

    watch_data = WatchData(
        watch_item_id=item.watch_item_id,
        vid_watch_time=payload.vid_watch_time,
        interval=1.0,
    )
    db.add(watch_data)
    db.flush()

    log_data = LogData(
        watch_data_id=watch_data.watch_data_id,
        fps_num=payload.fps_num,
        extraction_type=payload.extraction_type,
    )
    db.add(log_data)
    db.flush()

    db.add(
        ModelResult(
            log_data_id=log_data.log_data_id,
            model=payload.model_name,
            result=payload.focus_score,
        )
    )
    db.flush()

    item.current_time = payload.vid_watch_time
    scores = list(
        db.scalars(
            select(ModelResult.result)
            .join(LogData)
            .join(WatchData)
            .where(WatchData.watch_item_id == item.watch_item_id)
        ).all()
    )
    item.average_focus = sum(scores) / len(scores) if scores else payload.focus_score

    db.commit()
    db.refresh(item)
    return item, payload.focus_score


def end_session(db: Session, user: User, watch_item_id: int) -> WatchItem:
    item = get_owned_watch_item(db, user, watch_item_id)
    item.status = "ended"
    db.commit()
    db.refresh(item)
    return item


def list_history(db: Session, user: User) -> list[WatchHistoryItem]:
    items = list(
        db.scalars(
            select(WatchItem).where(WatchItem.user_id == user.user_id).order_by(WatchItem.last_updated.desc())
        ).all()
    )
    history: list[WatchHistoryItem] = []
    for item in items:
        video = db.scalar(select(Video).where(Video.youtube_id == item.youtube_id))
        history.append(
            WatchHistoryItem(
                watch_item_id=item.watch_item_id,
                youtube_id=item.youtube_id,
                video_name=video.name if video else None,
                status=item.status,
                current_time=item.current_time,
                average_focus=item.average_focus,
                last_updated=item.last_updated,
            )
        )
    return history
