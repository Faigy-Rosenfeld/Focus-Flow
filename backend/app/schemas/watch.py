from datetime import datetime

from pydantic import BaseModel, Field


class WatchSessionStart(BaseModel):
    youtube_id: str = Field(min_length=5, max_length=32)


class WatchItemPublic(BaseModel):
    watch_item_id: int
    user_id: int
    youtube_id: str
    current_time: float
    save_time: datetime
    last_updated: datetime
    status: str
    average_focus: float | None

    model_config = {"from_attributes": True}


class FocusSampleCreate(BaseModel):
    focus_score: float = Field(ge=0.0, le=1.0)
    vid_watch_time: float = Field(ge=0.0)
    fps_num: float = Field(default=1.0, gt=0)
    model_name: str = Field(default="v4_2", max_length=64)
    extraction_type: str = Field(default="face_landmarks", max_length=64)


class FocusSampleResponse(BaseModel):
    watch_item_id: int
    focus_score: float
    average_focus: float
    status: str


class WatchHistoryItem(BaseModel):
    watch_item_id: int
    youtube_id: str
    video_name: str | None = None
    status: str
    current_time: float
    average_focus: float | None
    last_updated: datetime
