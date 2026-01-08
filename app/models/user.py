from sqlalchemy import String, Integer, Boolean, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str] = mapped_column(String(60))
    middle_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    last_name: Mapped[str] = mapped_column(String(60))

    contact_number: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    occupation: Mapped[str] = mapped_column(String(40))
    country: Mapped[str] = mapped_column(String(80))

    password_hash: Mapped[str] = mapped_column(Text)

    subscription: Mapped[int] = mapped_column(Integer, default=0)  # 0 Free, 1 Pro
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    #
    # refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
    #     back_populates="user", cascade="all, delete-orphan"
    # )
