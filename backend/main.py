from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

app = FastAPI(title="INTAX Audit Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mongo
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("Mongo URI env var is not set (MONGODB_URI or MONGO_URI)")

client = MongoClient(MONGO_URI)
db = client["intax_db"]
collection = db["acceptance"]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/acceptance")
def create_acceptance(payload: dict):
    payload["created_at"] = datetime.utcnow()
    result = collection.insert_one(payload)
    return {"_id": str(result.inserted_id), "created_at": payload["created_at"]}

@app.get("/acceptance")
def list_acceptance():
    docs = list(collection.find())
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

@app.delete("/acceptance/{acceptance_id}")
def delete_acceptance(acceptance_id: str):
    result = collection.delete_one({"_id": ObjectId(acceptance_id)})
    return {"deleted": result.deleted_count}
