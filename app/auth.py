from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )







pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def safe_password(password: str):
    if len(password.encode("utf-8")) > 72:
        password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    if len(plain.encode("utf-8")) > 72:
        plain = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(plain, hashed)
