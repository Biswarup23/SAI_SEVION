from pydantic import BaseModel
from typing import Optional

class FeedbackCreate(BaseModel):
    message: str
    rating: int
    category: str
    app_version: str
    platform: str
    user_email: Optional[str] = None   # 👈 email from client


class FeedbackOut(BaseModel):
    feedback_uid: str
    status: str

    class Config:
        from_attributes = True
