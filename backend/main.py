from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="INTAX Audit Backend (V2)")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODELS ----------------
class AcceptanceIn(BaseModel):
    company_name: str
    client_type: Optional[str] = None
    revenue: Optional[str] = None
    total_assets: Optional[str] = None

class AcceptanceOut(AcceptanceIn):
    id: int
    created_at: datetime

# ---------------- FAKE DB ----------------
db: List[AcceptanceOut] = []

# ---------------- ROUTES ----------------
@app.get("/")
def root():
    return {"status": "INTAX Audit Backend V2 running"}

@app.get("/acceptance", response_model=List[AcceptanceOut])
def list_acceptance():
    return db

@app.post("/acceptance", response_model=AcceptanceOut)
def create_acceptance(data: AcceptanceIn):
    record = AcceptanceOut(
        id=len(db) + 1,
        created_at=datetime.utcnow(),
        **data.dict()
    )
    db.append(record)
    return record
@app.get("/health")
def health():
    return {"status": "ok"}
