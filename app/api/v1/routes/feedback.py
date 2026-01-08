import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackOut
from app.models.feedback import Feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])

# If you already have auth dependency, plug it here.
# For now: accept anonymous OR logged-in user id passed from token if available.
@router.post("", response_model=FeedbackOut)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    try:
        fb = Feedback(
            feedback_uid=str(uuid.uuid4()),
            user_id=None,                      # keep numeric user id for future auth
            user_email=payload.user_email,     # 👈 store email here
            message=payload.message,
            rating=payload.rating,
            category=payload.category,
            app_version=payload.app_version,
            platform=payload.platform,
        )
        db.add(fb)
        db.commit()
        db.refresh(fb)
        return {"feedback_uid": fb.feedback_uid, "status": fb.status}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {e}")
