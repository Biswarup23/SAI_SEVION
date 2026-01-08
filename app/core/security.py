import hashlib
from passlib.context import CryptContext

# Use bcrypt_sha256 to avoid the 72-byte limit problem
pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto",
)

def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return pwd_context.verify(pw, hashed)

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
