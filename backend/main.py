from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime

app = FastAPI(title="INTAX Audit Backend")

# -------------------------
# CORS (frontend-ээ дараа нь нэмэж болно)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # дараа нь frontend URL-ээр нарийсгана
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# MongoDB connection
# -------------------------
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is not set")

client = MongoClient(MONGO_URI)

# ⚠️ ЭНД Atlas дээрх DB нэрээ ЯГ тааруул
db = client["intax_db"]
collection = db["acceptance"]

# -------------------------
# Health check
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------
# CREATE acceptance (POST)
# --------------
