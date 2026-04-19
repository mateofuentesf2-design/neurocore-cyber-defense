from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    pwd = password[:72] if len(password) > 72 else password
    return pwd_context.hash(pwd)

def verify_password(plain, hashed):
    pwd = plain[:72] if len(plain) > 72 else plain
    return pwd_context.verify(pwd, hashed)