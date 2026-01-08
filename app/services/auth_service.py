from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import hash_password, verify_password, sha256
from app.core.tokens import make_access_token, make_refresh_token, make_verify_token, decode_token
from app.core.config import settings
from app.services.email_service import send_verification_email

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()

def signup(db: Session, payload) -> dict:
    email = payload.email.strip().lower()
    if get_user_by_email(db, email):
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        first_name=payload.first_name.strip(),
        middle_name=(payload.middle_name.strip() if payload.middle_name else None),
        last_name=payload.last_name.strip(),
        contact_number=payload.contact_number.strip(),
        email=email,
        occupation=payload.occupation.strip(),
        country=payload.country.strip(),
        password_hash=hash_password(payload.password),
        subscription=0,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    verify_token = make_verify_token(email)
    verify_link = f"{settings.APP_BASE_URL}/api/v1/auth/verify-email?token={verify_token}"
    send_verification_email(email, verify_link)

    return {"message": "Signup successful. Please verify your email, then login."}

def verify_email(db: Session, token: str) -> dict:
    try:
        data = decode_token(token)
        if data.get("type") != "verify":
            raise HTTPException(status_code=400, detail="Invalid token type")
        email = data.get("sub")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid/expired token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()
    return {"message": "Email verified. You can now login."}

def _store_refresh_token(db: Session, user_id: int, refresh_token: str):
    rec = RefreshToken(user_id=user_id, token_hash=sha256(refresh_token), revoked=False)
    db.add(rec)
    db.commit()

def _is_refresh_valid(db: Session, user_id: int, refresh_token: str) -> bool:
    h = sha256(refresh_token)
    rec = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.token_hash == h
    ).first()
    return bool(rec) and not rec.revoked

def _revoke_refresh(db: Session, user_id: int, refresh_token: str):
    h = sha256(refresh_token)
    rec = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.token_hash == h
    ).first()
    if rec:
        rec.revoked = True
        db.commit()

def login(db: Session, payload) -> dict:
    user = get_user_by_email(db, payload.email.lower())
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # if not user.is_verified:
    #     raise HTTPException(status_code=403, detail="Email not verified. Please verify before login.")

    access = make_access_token(user.email)
    refresh = make_refresh_token(user.email)
    _store_refresh_token(db, user.id, refresh)

    return {
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "contact_number": user.contact_number,
        "email": user.email,
        "occupation": user.occupation,
        "country": user.country,
        "subscription": user.subscription,
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }

def refresh_access(db: Session, refresh_token: str) -> dict:
    try:
        data = decode_token(refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        email = data.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid/expired refresh token")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not _is_refresh_valid(db, user.id, refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token revoked or not recognized")

    access = make_access_token(user.email)
    return {"access_token": access, "token_type": "bearer"}

def logout(db: Session, refresh_token: str) -> dict:
    try:
        data = decode_token(refresh_token)
        email = data.get("sub")
    except Exception:
        return {"message": "Logged out"}

    user = get_user_by_email(db, email)
    if not user:
        return {"message": "Logged out"}

    _revoke_refresh(db, user.id, refresh_token)
    return {"message": "Logged out"}
