from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

app = FastAPI(title="INTAX Audit Backend", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # дараа нь frontend domain-оор хязгаарлана
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# MongoDB connection
# -------------------------
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or os.getenv("MONGO_URL")
if not MONGO_URI:
    raise RuntimeError("Mongo URI env var is not set (MONGODB_URI or MONGO_URI)")

client = MongoClient(MONGO_URI)

# DB сонголт
db = client["intax_db"]
collection = db["acceptance"]

# Эхлэх үед DB ping (auth/URI алдаа байвал энд унаж ойлгомжтой болно)
try:
    client.admin.command("ping")
except Exception as e:
    raise RuntimeError(f"MongoDB connection failed: {e}")


def to_json(doc: dict) -> dict:
    """Mongo document-ыг JSON буцаалтанд тохируулж хөрвүүлнэ."""
    if not doc:
        return doc
    doc["_id"] = str(doc.get("_id"))
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/acceptance")
def create_acceptance(payload: dict):
    try:
        doc = {
            "company_name": payload.get("company_name"),
            "year": payload.get("year"),
            "auditor": payload.get("auditor"),
            "created_at": datetime.utcnow(),
        }

        # company_name байхгүй бол 422 биш, өөрсдөө ойлгомжтой error өгье
        if not doc["company_name"]:
            raise HTTPException(status_code=400, detail="company_name is required")

        result = collection.insert_one(doc)

        # Response дээр created_at-ийг string болгож буцаана
        return {
            "_id": str(result.inserted_id),
            "company_name": doc["company_name"],
            "year": doc["year"],
            "auditor": doc["auditor"],
            "created_at": doc["created_at"].isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/acceptance")
def list_acceptance():
    try:
        docs = list(collection.find().sort("created_at", -1))
        return [to_json(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/acceptance/{acceptance_id}")
def delete_acceptance(acceptance_id: str):
    try:
        result = collection.delete_one({"_id": ObjectId(acceptance_id)})
        return {"deleted": result.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
