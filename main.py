from fastapi import FastAPI, HTTPException
from tortoise.contrib.fastapi import register_tortoise
from models.iqama import IqamaRecord
from db.settings import TORTOISE_ORM
from routes import customers  # ✅ Import your new router
import os
from dotenv import load_dotenv
from routes import admin
# ✅ Step 1.1: Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from routes import theme_settings
from routes import absher
from routes import iqama
from routes import mpin
from routes import account_details  # if not already imported
from routes import portfolio_summary
from routes import card_details
from routes import transaction_summary
from routes import transactions 
from routes import international_transactions

load_dotenv(dotenv_path=".env")
print("Using DB:", os.getenv("DATABASE_URL"))

app = FastAPI()

# ✅ Step 1.2: Define allowed origins and add the middleware
# This should be placed right after `app = FastAPI()`
origins = [
    "http://localhost",
    "http://localhost:3000",  # Your React admin portal
    "http://localhost:5173",  # ✅ ADD THIS LINE for your new Vite admin portal
    #"https://admin-frontend-llsr.onrender.com",  # ✅ ADD THIS LINE for your deployed admin portal
    "https://banking-admin-new.onrender.com", 
    # Add any other origins you might deploy to
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # ... rest of the middleware config ...
)

# ... (the rest of your main.py file) ...

# ✅ Include customers router
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(theme_settings.router)
app.include_router(absher.router, prefix="/admin", tags=["Absher"])
app.include_router(iqama.router, prefix="/iqama")
app.include_router(mpin.router)
app.include_router(account_details.router, prefix="/api")
app.include_router(portfolio_summary.router, prefix="/api")
app.include_router(card_details.router, prefix="/api")
app.include_router(transaction_summary.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(international_transactions.router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "ok", "service": "banking-backend-new"}

#@app.post("/validate-iqama")
#async def validate_iqama(data: dict):
#    iqama_id = data.get("iqama_id")
#    mobile_number = data.get("mobile_number")

#    if not iqama_id or not mobile_number:
#        raise HTTPException(status_code=400, detail="Iqama ID and Mobile Number required")
#
#    record = await IqamaRecord.get_or_none(iqama_id=iqama_id)
#    if not record:
#        raise HTTPException(status_code=404, detail="Iqama ID not found")

#    if record.mobile_number != mobile_number:
#        raise HTTPException(status_code=400, detail="Mobile number does not match")

#    return {
#        "message": "Iqama ID and mobile number validated",
#        "full_name": record.full_name,
#        "gender": record.gender,
#        "city": record.city
#    }

@app.get("/iqama-details/{iqama_id}")
async def get_iqama_details(iqama_id: str):
    record = await IqamaRecord.get_or_none(iqama_id=iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Iqama ID not found")
    return record

# ✅ Register Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # ✅ Change this to True temporarily,
    add_exception_handlers=True,
)
