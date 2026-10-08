from datetime import datetime

from pydantic import BaseModel, Field


class VideoCreate(BaseModel):
    youtube_id: str = Field(min_length=5, max_length=32)
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    subject_name: str = "general"
    length_seconds: int = Field(default=0, ge=0)


class VideoUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    subject_name: str | None = None
    length_seconds: int | None = Field(default=None, ge=0)


class VideoPublic(BaseModel):
    video_id: int
    youtube_id: str
    upload_by: int | None
    name: str
    description: str
    subject_name: str
    added_date: datetime
    length_seconds: int

    model_config = {"from_attributes": True}
