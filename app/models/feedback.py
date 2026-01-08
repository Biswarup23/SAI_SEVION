from sqlalchemy import Column, BigInteger, String, Text, DateTime, Enum, SmallInteger
from sqlalchemy.sql import func
from app.db.base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    feedback_uid = Column(String(36), unique=True, index=True, nullable=False)

    user_id = Column(BigInteger, index=True, nullable=True)   # numeric user id (future)
    user_email = Column(String(255), index=True, nullable=True)  # 👈 store email here

    rating = Column(SmallInteger, nullable=True)
    category = Column(String(40), nullable=True)
    message = Column(Text, nullable=False)

    app_version = Column(String(30), nullable=True)
    platform = Column(String(30), nullable=True)

    status = Column(Enum("new", "reviewed", "closed"), nullable=False, server_default="new")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
