from sqlalchemy import Integer, Boolean, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)   # <-- no FK

    token_hash: Mapped[str] = mapped_column(String(64), index=True)  # SHA256
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
