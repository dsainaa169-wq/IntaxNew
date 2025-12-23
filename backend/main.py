from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime, timezone
import os

from pymongo import MongoClient
from bson import ObjectId


# ---------------- APP ----------------
app = FastAPI(title="INTAX Audit Backend (V2)")


# ---------------- CORS ----------------
# Frontend-ийн чинь Render domain-оо нэмээрэй (байгаагүй бол)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # "https://<your-frontend>.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- DB (MongoDB Atlas) ----------------
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "intax_db")

if not MONGODB_URI:
    # Render дээр env var тавиагүй бол энд унаж болно.
    # (local дээр .env ашиглах бол python-dotenv нэмж болно)
    raise RuntimeError("MONGODB_URI is not set in environment variables")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
acceptance_col = db["acceptance"]


# ---------------- HELPERS ----------------
def to_out(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Mongo doc -> API output"""
    return {
        "_id": str(doc["_id"]),
        "client_name": doc.get("client_name", ""),
        "year": doc.get("year", ""),
        "created_at": doc.get("created_at"),
    }


# ---------------- MODELS ----------------
class AcceptanceIn(BaseModel):
    client_name: str = Field(..., min_length=1)
    year: str = Field(..., min_length=1)


class AcceptanceOut(BaseModel):
    _id: str
    client_name: str
    year: str
    created_at: Optional[datetime] = None


# ---------------- ROUTES ----------------
@app.get("/")
def root():
    return {"status": "INTAX Audit Backend V2 running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/acceptance", response_model=List[AcceptanceOut])
def list_acceptance():
    docs = list(acceptance_col.find().sort("created_at", -1))
    return [to_out(d) for d in docs]


@app.post("/acceptance", response_model=AcceptanceOut)
def create_acceptance(data: AcceptanceIn):
    doc = {
        "client_name": data.client_name,
        "year": data.year,
        "created_at": datetime.now(timezone.utc),
    }
    result = acceptance_col.insert_one(doc)
    saved = acceptance_col.find_one({"_id": result.inserted_id})
    return to_out(saved)


@app.delete("/acceptance/{id}")
def delete_acceptance(id: str):
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")

    res = acceptance_col.delete_one({"_id": oid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")

    return {"deleted": True, "id": id}
