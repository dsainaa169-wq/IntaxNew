# auth.py
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ⚠️ Түр placeholder: чи дараа нь Mongo-оос хайдаг болгоно
def find_user(email: str, password: str):
    # TODO: энд MongoDB users collection-оос хайх логик чинь байх ёстой
    # Түр тест:
    if email == "admin@test.com" and password == "123":
        return {"email": email, "name": "Admin", "role": "admin"}
    if email == "auditor@test.com" and password == "123":
        return {"email": email, "name": "Auditor", "role": "auditor"}
    return None

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = find_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({
        "sub": user["email"],
        "role": user["role"],
        "name": user["name"]
    })
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "role": role, "name": payload.get("name")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_roles(*allowed_roles: str):
    def guard(user=Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return guard
