import os
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from pymongo import MongoClient
from bson import ObjectId

from jose import jwt, JWTError


# =========================
# App
# =========================
app = FastAPI(title="INTAX Audit Backend (Python)", version="0.1.0")

# CORS (дараа нь frontend domain-оор хязгаарлаарай)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Mongo
# =========================
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or os.getenv("MONGO_URL")
if not MONGO_URI:
    raise RuntimeError("Mongo URI env var is not set (MONGODB_URI or MONGO_URI or MONGO_URL)")

client = MongoClient(MONGO_URI)
db = client["intax_db"]
collection = db["acceptance"]

# Эхлэх үед DB ping (URI/auth алдаа байвал эндээс шууд мэдэгдэнэ)
try:
    client.admin.command("ping")
except Exception as e:
    raise RuntimeError(f"MongoDB connection failed: {e}")


def to_json(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Mongo document-ыг JSON friendly болгоно."""
    if not doc:
        return doc

    # _id -> string
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])

    # frontend-д амар (нэг стандарт id)
    doc["id"] = doc.get("id") or doc.get("_id")

    # datetime -> isoformat
    for k in ["created_at", "updated_at"]:
        if isinstance(doc.get(k), datetime):
            doc[k] = doc[k].isoformat()

    return doc


# =========================
# Auth (JWT)
# =========================
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")  # Render дээр заавал сольж өг
JWT_ALG = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ADMIN_EMAIL = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or ""
AUDITOR_EMAIL = (os.getenv("AUDITOR_EMAIL") or "").strip().lower()
AUDITOR_PASSWORD = os.getenv("AUDITOR_PASSWORD") or ""


def find_user(email: str, password: str) -> Optional[dict]:
    email = (email or "").strip().lower()

    if ADMIN_EMAIL and ADMIN_PASSWORD and email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        return {"email": ADMIN_EMAIL, "role": "admin", "name": "Admin"}

    if AUDITOR_EMAIL and AUDITOR_PASSWORD and email == AUDITOR_EMAIL and password == AUDITOR_PASSWORD:
        return {"email": AUDITOR_EMAIL, "role": "auditor", "name": "Auditor"}

    return None


def create_token(payload: dict) -> str:
    exp = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    to_encode = {**payload, "exp": exp}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)


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


# =========================
# Health
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# Auth endpoints
# =========================
@app.post("/auth/login")
def login(payload: dict):
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    user = find_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({"sub": user["email"], "role": user["role"], "name": user["name"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"],
        "email": user["email"],
    }


@app.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    return {"email": user["sub"], "role": user["role"], "name": user.get("name")}


# =========================
# Acceptance CRUD (Protected)
# =========================
@app.post("/acceptance")
def create_acceptance(payload: dict, user: dict = Depends(require_roles("admin", "auditor"))):
    company_name = payload.get("company_name") or payload.get("companyName")
    year = payload.get("year")
    auditor = payload.get("auditor")

    if not company_name:
        raise HTTPException(status_code=400, detail="company_name is required")

    doc = {
        "company_name": company_name,
        "year": year,
        "auditor": auditor,
        "status": payload.get("status", "new"),
        "created_at": datetime.utcnow(),
        "created_by": user["sub"],
    }

    result = collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc["id"] = doc["_id"]
    doc["created_at"] = doc["created_at"].isoformat()
    return doc


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
    payload.pop("id", None)

    try:
        oid = ObjectId(acceptance_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid acceptance_id")

    payload["updated_at"] = datetime.utcnow()
    payload["updated_by"] = user["sub"]

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
