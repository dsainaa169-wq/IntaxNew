from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import os

from pymongo import MongoClient
from bson import ObjectId

# ---------------- APP ----------------
app = FastAPI(title="INTAX Audit Backend")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "https://intaxnew.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DB ----------------
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "intax_db")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
acceptance_col = db["acceptance"]

# ---------------- MODELS ----------------
class AcceptanceIn(BaseModel):
    company_name: str

class AcceptanceOut(BaseModel):
    _id: str
    company_name: str
    created_at: Optional[datetime]

# ---------------- HELPERS ----------------
def serialize(doc):
    return {
        "_id": str(doc["_id"]),
        "company_name": doc.get("company_name"),
        "created_at": doc.get("created_at"),
    }

# ---------------- ROUTES ----------------
@app.get("/")
def root():
    return {"status": "INTAX Audit Backend running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/acceptance", response_model=List[AcceptanceOut])
def list_acceptance():
    docs = list(acceptance_col.find().sort("created_at", -1))
    return [serialize(d) for d in docs]

@app.post("/acceptance", response_model=AcceptanceOut)
def create_acceptance(data: AcceptanceIn):
    doc = {
        "company_name": data.company_name,
        "created_at": datetime.now(timezone.utc),
    }
    res = acceptance_col.insert_one(doc)
    saved = acceptance_col.find_one({"_id": res.inserted_id})
    return serialize(saved)

@app.delete("/acceptance/{id}")
def delete_acceptance(id: str):
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")

    result = acceptance_col.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not found")

    return {"deleted": True, "id": id}
