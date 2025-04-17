from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import uuid

app = FastAPI(title="April 17th Salesforce-Alike CRM")

# --- In-Memory DB Substitute ---
merchants_db = {}
deals_db = {}

# --- Data Models ---
class Merchant(BaseModel):
    id: str
    name: str
    vertical: Optional[str]
    monthly_volume: float
    current_rate: float
    platform: Optional[str]
    notes: Optional[str] = ""

class Deal(BaseModel):
    id: str
    merchant_id: str
    proposed_rate: float
    recurring: bool
    lending_flag: bool
    quote_generated: bool = False
    created_at: date

# --- Helper Functions ---
def generate_id():
    return str(uuid.uuid4())

# --- Merchant Routes ---
@app.post("/merchants/", response_model=Merchant)
def create_merchant(merchant: Merchant):
    if merchant.id in merchants_db:
        raise HTTPException(status_code=400, detail="Merchant already exists")
    merchants_db[merchant.id] = merchant
    return merchant

@app.get("/merchants/", response_model=List[Merchant])
def list_merchants():
    return list(merchants_db.values())

# --- Deal Routes ---
@app.post("/deals/", response_model=Deal)
def create_deal(deal: Deal):
    if deal.id in deals_db:
        raise HTTPException(status_code=400, detail="Deal already exists")
    if deal.merchant_id not in merchants_db:
        raise HTTPException(status_code=404, detail="Merchant not found")
    deals_db[deal.id] = deal
    return deal

@app.get("/deals/", response_model=List[Deal])
def list_deals():
    return list(deals_db.values())

# --- Quote Engine ---
@app.get("/quote/{merchant_id}")
def generate_quote(merchant_id: str):
    merchant = merchants_db.get(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    stripe_rate = 0.037  # Stripe + recurring fee
    alp_rate = 0.025
    stripe_fee = merchant.monthly_volume * stripe_rate
    alp_fee = merchant.monthly_volume * alp_rate
    savings = stripe_fee - alp_fee

    lending_angle = ""
    if merchant.monthly_volume >= 20000:
        lending_angle = "Suggest SBA via RateTracker"
    elif merchant.monthly_volume >= 5000:
        lending_angle = "Suggest Term Loan"
    else:
        lending_angle = "Focus on cost savings only"

    return {
        "merchant": merchant.name,
        "stripe_fee": f"${stripe_fee:,.2f}",
        "alp_fee": f"${alp_fee:,.2f}",
        "monthly_savings": f"${savings:,.2f}",
        "annual_savings": f"${savings*12:,.2f}",
        "lending_suggestion": lending_angle
    }

# --- Root ---
@app.get("/")
def root():
    return {"message": "Welcome to the April 17th Salesforce-Alike CRM"}
