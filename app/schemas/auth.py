from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    middle_name: str | None = Field(default=None, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)

    contact_number: str = Field(min_length=6, max_length=30)
    email: EmailStr

    occupation: str = Field(min_length=1, max_length=40)
    country: str = Field(min_length=1, max_length=80)

    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class ProfileResponse(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    contact_number: str | None = None
    email: EmailStr
    occupation: str | None = None
    country: str | None = None
    subscription: int = 0

class TokenResponse(ProfileResponse):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str
