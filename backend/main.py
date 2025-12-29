from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional
import os

app = FastAPI(title="INTAX Audit Backend (Python)", version="0.1.0")

# -------------------------
# CORS (production safe)
# -------------------------
# ✅ Render дээр FRONTEND_ORIGIN env өгч болно:
# FRONTEND_ORIGIN=https://your-frontend-domain.com
frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip()

# local + optional production origin
origins = ["http://localhost:5173"]
if frontend_origin:
    origins.append(frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # ❗ "*" биш
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Mongo
# -------------------------
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or os.getenv("MONGO_URL")
if not MONGO_URI:
    raise RuntimeError("Mongo URI env var is not set (MONGODB_URI or MONGO_URI)")

client = MongoClient(MONGO_URI)
db = client["intax_db"]
collection = db["acceptance"]

# Ping шалгалт
try:
    client.admin.command("ping")
except Exception as e:
    raise RuntimeError(f"MongoDB connection failed: {e}")

# -------------------------
# Auth (JWT)
# -------------------------
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is not set")

JWT_ALG = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))

# ✅ Swagger-ийн Authorize зөв ажиллуулахын тулд tokenUrl нь login endpoint-тэй яг таарах ёстой
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

USERS = [
    {
        "email": (os.getenv("ADMIN_EMAIL") or "").strip().lower(),
        "password": os.getenv("ADMIN_PASSWORD") or "",
        "role": "admin",
        "name": "Admin",
    },
    {
        "email": (os.getenv("AUDITOR_EMAIL") or "").strip().lower(),
        "password": os.getenv("AUDITOR_PASSWORD") or "",
        "role": "auditor",
        "name": "Auditor",
    },
]

def find_user(email: str, password: str) -> Optional[dict]:
    email = (email or "").strip().lower()
    for u in USERS:
        if u["email"] and u["password"] and u["email"] == email and u["password"] == password:
            return u
    return None

def create_token(payload: dict) -> str:
    exp = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode = {**payload, "exp": exp}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def to_json(doc: dict) -> dict:
    if not doc:
        return doc
    doc["_id"] = str(doc.get("_id"))
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    if isinstance(doc.get("updated_at"), datetime):
        doc["updated_at"] = doc["updated_at"].isoformat()
    return doc

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        if "sub" not in data or "role" not in data:
            raise HTTPException(status_code=401, detail="Invalid token")
        return data
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def require_roles(*roles: str):
    def _dep(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep

# -------------------------
# Basic endpoints
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------
# Auth endpoints
# -------------------------
# ✅ ОДОО: OAuth2PasswordRequestForm ашиглана
# Энэ нь frontend-ээс application/x-www-form-urlencoded хэлбэрээр username/password явуулахыг шаарддаг
@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    email = (form.username or "").strip().lower()
    password = form.password or ""

    user = find_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": user["email"], "role": user["role"], "name": user["name"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "name": user["name"]}

@app.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return {"email": user["sub"], "role": user["role"], "name": user.get("name")}

# -------------------------
# Acceptance endpoints (protected)
# -------------------------
@app.post("/acceptance")
def create_acceptance(payload: dict, user: dict = Depends(require_roles("admin", "auditor"))):
    payload["created_at"] = datetime.utcnow()
    payload["created_by"] = user["sub"]
    payload.setdefault("status", "new")
    result = collection.insert_one(payload)
    doc = collection.find_one({"_id": result.inserted_id})
    return to_json(doc)

@app.get("/acceptance")
def list_acceptance(user: dict = Depends(require_roles("admin", "auditor"))):
    docs = list(collection.find().sort("created_at", -1))
    return [to_json(d) for d in docs]

@app.get("/acceptance/{acceptance_id}")
def get_acceptance(acceptance_id: str, user: dict = Depends(require_roles("admin", "auditor"))):
    try:
        oid = ObjectId(acceptance_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid acceptance_id")

    doc = collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return to_json(doc)

@app.put("/acceptance/{acceptance_id}")
def update_acceptance(acceptance_id: str, payload: dict, user: dict = Depends(require_roles("admin", "auditor"))):
    payload.pop("_id", None)
    payload["updated_at"] = datetime.utcnow()
    payload["updated_by"] = user["sub"]

    try:
        oid = ObjectId(acceptance_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid acceptance_id")

    result = collection.update_one({"_id": oid}, {"$set": payload})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")

    doc = collection.find_one({"_id": oid})
    return to_json(doc)

@app.delete("/acceptance/{acceptance_id}")
def delete_acceptance(acceptance_id: str, user: dict = Depends(require_roles("admin"))):
    try:
        oid = ObjectId(acceptance_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid acceptance_id")

    result = collection.delete_one({"_id": oid})
    return {"deleted": result.deleted_count}
