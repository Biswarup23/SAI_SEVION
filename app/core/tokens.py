from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

def _now():
    return datetime.now(timezone.utc)

def make_access_token(email: str) -> str:
    exp = _now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": email, "type": "access", "exp": exp}, settings.JWT_SECRET, algorithm="HS256")

def make_refresh_token(email: str) -> str:
    exp = _now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": email, "type": "refresh", "exp": exp}, settings.JWT_SECRET, algorithm="HS256")

def make_verify_token(email: str) -> str:
    exp = _now() + timedelta(minutes=settings.VERIFY_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": email, "type": "verify", "exp": exp}, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
