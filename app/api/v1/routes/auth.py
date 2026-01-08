from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, RefreshRequest, LogoutRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    return auth_service.signup(db, payload)

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    return auth_service.verify_email(db, token)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, payload)

@router.post("/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access(db, payload.refresh_token)

@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    return auth_service.logout(db, payload.refresh_token)
