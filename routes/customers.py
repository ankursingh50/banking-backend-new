from fastapi import APIRouter, HTTPException, Request
from models.customer import OnboardedCustomer
from models.iqama import IqamaRecord
from reference_utils import generate_dep_reference_number
from datetime import datetime, date
from tortoise import timezone
from utils.security import hash_mpin
from utils.security import verify_password
from pydantic import BaseModel
from typing import Optional
import traceback

router = APIRouter()

# Helper to strip timezone info safely
def strip_tz(dt):
    if isinstance(dt, datetime):
        return dt.replace(tzinfo=None)
    return dt

# Request schema for onboarding start
class StartOnboardingRequest(BaseModel):
    iqama_id: str
    device_id: Optional[str]
    device_type: Optional[str]
    location: Optional[str]
    current_step: Optional[str] = None

# Request schema for update
class UpdateCustomerRequest(BaseModel):
    building_number: Optional[str]
    street: Optional[str]
    neighbourhood: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    device_id: Optional[str]
    device_type: Optional[str]
    location: Optional[str]
    status: Optional[str]
    pep_flag: Optional[str]
    tax_employer_flag: Optional[str]
    disability_flag: Optional[str]
    high_risk_flag: Optional[str]
    account_purpose: Optional[str]
    estimated_withdrawal: Optional[float]
    mpin: Optional[str]
    password: Optional[str]
    current_step: Optional[str]
    additional_mobile_number: Optional[str]
    #employment_status: Optional[str]
    source_of_income: Optional[str]
    employment_sector: Optional[str]
    #industry: Optional[str]
    salary_income: Optional[str]
    business_income: Optional[str]
    investment_income: Optional[str]
    rental_income: Optional[str]
    personal_allowance: Optional[str]
    pension_income: Optional[str]
    #other_income: Optional[str]
    employer_industry: Optional[str]
    business_industry: Optional[str]
    hafiz_income: Optional[str]
    unemployed_income: Optional[str]
    housewife_allowance: Optional[str]
    student_allowance: Optional[str]

# ⬇️ POST /customers/start
@router.post("/start")
async def start_customer_onboarding(data: StartOnboardingRequest):
    existing = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)

    if existing:
        if existing.status == "Account Successfully Created":
            raise HTTPException(status_code=400, detail="Iqama already onboarded")

        # ✅ Invalidate old device if needed
        resumed_on_new_device = False
        if existing.device_id and existing.device_id != data.device_id:
            existing.status = "Started on another device"
            existing.device_id = None
            existing.updated_at = timezone.now()
            await existing.save()
            resumed_on_new_device = True

        # 🔄 Update the existing record with the new device details
        existing.device_id = data.device_id
        existing.device_type = data.device_type
        existing.location = data.location
        existing.status = "in_progress"
        existing.current_step = data.current_step or "nafath"
        existing.updated_at = timezone.now()
        await existing.save()

        return {
            "resumed_on_new_device": resumed_on_new_device,
            "record": existing
        }

    # 🔍 Lookup from iqama_records
    iqama = await IqamaRecord.get_or_none(iqama_id=data.iqama_id)
    if not iqama:
        raise HTTPException(status_code=404, detail="Iqama ID not found in records")

    # Generate DEP reference number
    dep_ref = await generate_dep_reference_number()

    # 🚀 Start onboarding for the new iqama_id
    record = await OnboardedCustomer.create(
        iqama_id=iqama.iqama_id,
        full_name=iqama.full_name,
        arabic_name=iqama.arabic_name,
        mobile_number=iqama.mobile_number,
        date_of_birth=strip_tz(iqama.date_of_birth),
        date_of_birth_hijri=str(iqama.dob_hijri) if iqama.dob_hijri else None,
        expiry_date=strip_tz(iqama.expiry_date),
        expiry_date_hijri=iqama.expiry_date_hijri,
        issue_date=strip_tz(iqama.issue_date),
        age=(
            date.today().year - iqama.date_of_birth.year
            - ((date.today().month, date.today().day) < (iqama.date_of_birth.month, iqama.date_of_birth.day))
        ) if iqama.date_of_birth else None,
        gender=iqama.gender,
        nationality=iqama.nationality,
        building_number=iqama.building_number,
        street=iqama.street,
        neighbourhood=iqama.neighbourhood,
        city=iqama.city,
        postal_code=iqama.postal_code,
        country=iqama.country,
        dep_reference_number=dep_ref,
        device_id=data.device_id,
        device_type=data.device_type,
        location=data.location,
        status="in_progress",
        current_step=data.current_step or "nafath"
    )

    return {
        "resumed_on_new_device": False,
        "record": record
    }



class PasswordVerificationRequest(BaseModel):
    iqama_id: str
    password: str

class LoginRequest(BaseModel):
    iqama_id: Optional[str] = None
    mobile: Optional[str] = None
    password: str

@router.post("/verify-password")
async def verify_password_route(data: LoginRequest):
    user = None

    if data.iqama_id:
        user = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)
    if not user and data.mobile:
        user = await OnboardedCustomer.get_or_none(mobile_number=data.mobile)

    if not user or not user.password:
        raise HTTPException(status_code=404, detail="User or password not found")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "message": "Password verified",
        "iqama_id": user.iqama_id,
        "status": user.status,
        "current_step": user.current_step
    }


class IqamaDOBValidationRequest(BaseModel):
    iqama_id: str
    calendar_type: str  # 'gregorian' or 'hijri'
    dob: str            # in format: "DD Month YYYY"

@router.post("/validate-reset-request")
async def validate_reset_request(data: IqamaDOBValidationRequest):
    user = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)

    if not user:
        raise HTTPException(status_code=404, detail="Customer with this Iqama ID does not exist")

    if user.status != "Account Successfully Created":
        raise HTTPException(status_code=403, detail="Customer account is not ready for reset")

    if data.calendar_type == "gregorian":
        if user.date_of_birth.strftime("%d %B %Y") != data.dob:
            raise HTTPException(status_code=400, detail="Your ID/Iqama Number and Date of Birth does not match")
    elif data.calendar_type == "hijri":
        if user.date_of_birth_hijri != data.dob:
            raise HTTPException(status_code=400, detail="Your ID/Iqama Number and Date of Birth does not match")
    else:
        raise HTTPException(status_code=400, detail="Invalid calendar type")

    return {"message": "Validation passed"}

# ⬇️ GET /customers/onboarded
@router.get("/onboarded")
async def get_onboarded_customers():
    return await OnboardedCustomer.all().order_by("-created_at").values(
        "full_name",
        "iqama_id",
        "mobile_number",
        "device_id",
        "dep_reference_number",
        "created_at",
        "status",
        "current_step"
    )

# ⬇️ GET /customers/device/{device_id}
@router.get("/device/{device_id}")
async def get_customer_by_device(device_id: str):
    customer = await OnboardedCustomer.filter(
        device_id=device_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="No onboarding record found")

    return {
        "iqama_id": customer.iqama_id,
        "current_step": customer.current_step,
        "status": customer.status
    }

class DeviceUpdateRequest(BaseModel):
    iqama_id: Optional[str] = None
    mobile: Optional[str] = None
    device_id: str
    device_type: Optional[str] = None
    location: Optional[str] = None

#Update Device Information
@router.post("/update-device")
async def update_device_info(data: DeviceUpdateRequest):
    user = None

    if data.iqama_id:
        user = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)
    if not user and data.mobile:
        user = await OnboardedCustomer.get_or_none(mobile_number=data.mobile)

    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")

    user.device_id = data.device_id
    user.device_type = data.device_type
    user.location = data.location
    user.updated_at = timezone.now()
    await user.save()

    return {
        "message": "Device information updated",
        "iqama_id": user.iqama_id,
        "device_id": user.device_id
    }

# ⬇️ GET /customers/{iqama_id}
@router.get("/{iqama_id}")
async def get_customer(iqama_id: str):
    record = await OnboardedCustomer.get_or_none(iqama_id=iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer record not found")

    return {
        "iqama_id": record.iqama_id,
        "full_name": record.full_name,
        "arabic_name": record.arabic_name,
        "mobile_number": record.mobile_number,
        "dep_reference_number": record.dep_reference_number,
        "status": record.status,
        "created_at": record.created_at,
        "date_of_birth": record.date_of_birth,
        "date_of_birth_hijri": record.date_of_birth_hijri,
        "expiry_date": record.expiry_date,
        "expiry_date_hijri": record.expiry_date_hijri,
        "issue_date": record.issue_date,
        "age": record.age,
        "gender": record.gender,
        "nationality": record.nationality,
        "building_number": record.building_number,
        "street": record.street,
        "neighbourhood": record.neighbourhood,
        "city": record.city,
        "postal_code": record.postal_code,
        "country": record.country,
        "device_id": record.device_id,
        "device_type": record.device_type,
        "location": record.location,
        "account_purpose": record.account_purpose,
        "estimated_withdrawal": record.estimated_withdrawal,
        "pep_flag": record.pep_flag,
        "disability_flag": record.disability_flag,
        "tax_residency_outside_ksa": record.tax_residency_outside_ksa,
        #"employment_status": record.employment_status,
        "source_of_income": record.source_of_income,
        "employment_sector": record.employment_sector,
        #"industry": record.industry,
        "salary_income": record.salary_income,
        "business_income": record.business_income,
        "investment_income": record.investment_income,
        "rental_income": record.rental_income,
        #"personal_allowance": record.personal_allowance,
        "pension_income": record.pension_income,
        #"other_income": record.other_income,
        "employer_industry": record.employer_industry,
        "business_industry": record.business_industry,
        "hafiz_income": record.hafiz_income,
        "unemployed_income": record.unemployed_income,
        "housewife_allowance": record.housewife_allowance,
        "student_allowance": record.student_allowance,
        "device_registration_date": record.device_registration_date,
        "device_registration_time": record.device_registration_time,
        "password_set_date": record.password_set_date,
        "password_set_time": record.password_set_time,
        "mpin_set_date": record.mpin_set_date,
        "mpin_set_time": record.mpin_set_time,
    }

# ⬇️ GET /customers/{mobile number}
@router.get("/by-mobile/{mobile_number}")
async def get_customer_by_mobile(mobile_number: str):
    record = await OnboardedCustomer.get_or_none(mobile_number=mobile_number)
    if not record:
        raise HTTPException(status_code=404, detail="Customer record not found")

    return {
        "iqama_id": record.iqama_id,
        "full_name": record.full_name,
        "arabic_name": record.arabic_name,
        "mobile_number": record.mobile_number,
        "dep_reference_number": record.dep_reference_number,
        "status": record.status,
        "created_at": record.created_at,
        "date_of_birth": record.date_of_birth,
        "date_of_birth_hijri": record.date_of_birth_hijri,
        "expiry_date": record.expiry_date,
        "expiry_date_hijri": record.expiry_date_hijri,
        "issue_date": record.issue_date,
        "age": record.age,
        "gender": record.gender,
        "nationality": record.nationality,
        "building_number": record.building_number,
        "street": record.street,
        "neighbourhood": record.neighbourhood,
        "city": record.city,
        "postal_code": record.postal_code,
        "country": record.country,
        "device_id": record.device_id,
        "device_type": record.device_type,
        "location": record.location,
        "account_purpose": record.account_purpose,
        "estimated_withdrawal": record.estimated_withdrawal,
        "pep_flag": record.pep_flag,
        "disability_flag": record.disability_flag,
        "tax_residency_outside_ksa": record.tax_residency_outside_ksa,
        "source_of_income": record.source_of_income,
        "employment_sector": record.employment_sector,
        "salary_income": record.salary_income,
        "business_income": record.business_income,
        "investment_income": record.investment_income,
        "rental_income": record.rental_income,
        "pension_income": record.pension_income,
        "employer_industry": record.employer_industry,
        "business_industry": record.business_industry,
        "hafiz_income": record.hafiz_income,
        "unemployed_income": record.unemployed_income,
        "housewife_allowance": record.housewife_allowance,
        "student_allowance": record.student_allowance,
        "device_registration_date": record.device_registration_date,
        "device_registration_time": record.device_registration_time,
        "password_set_date": record.password_set_date,
        "password_set_time": record.password_set_time,
        "mpin_set_date": record.mpin_set_date,
        "mpin_set_time": record.mpin_set_time,
    }

class DeviceRegistrationUpdateRequest(BaseModel):
    iqama_id: str
    date: date
    time: str  # format "HH:MM:SS"

#update device registration timestamp
@router.put("/update-device-registration")
async def update_device_registration(data: DeviceRegistrationUpdateRequest):
    record = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Convert time string to time object
    try:
        time_obj = datetime.strptime(data.time, "%H:%M:%S").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")

    record.device_registration_date = data.date
    record.device_registration_time = time_obj
    record.updated_at = timezone.now()
    await record.save()

    return {"message": "Device registration timestamp updated successfully"}

class PasswordSetTimestampRequest(BaseModel):
    iqama_id: str
    date: date
    time: str  # format "HH:MM:SS"

#update password set timestamp
@router.put("/update-password-set-time")
async def update_password_set_time(data: PasswordSetTimestampRequest):
    record = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        time_obj = datetime.strptime(data.time, "%H:%M:%S").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")

    record.password_set_date = data.date
    record.password_set_time = time_obj
    record.updated_at = timezone.now()
    await record.save()

    return {"message": "Password set timestamp updated successfully"}

class MPINSetTimestampRequest(BaseModel):
    iqama_id: str
    date: date
    time: str  # format "HH:MM:SS"

#update mpin set timestamp
@router.put("/update-mpin-set-time")
async def update_mpin_set_time(data: MPINSetTimestampRequest):
    record = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        time_obj = datetime.strptime(data.time, "%H:%M:%S").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")

    record.mpin_set_date = data.date
    record.mpin_set_time = time_obj
    record.updated_at = timezone.now()
    await record.save()

    return {"message": "MPIN set timestamp updated successfully"}

class ExpiryDateUpdateRequest(BaseModel):
    iqama_id: str
    expiry_date: str
    expiry_date_hijri: Optional[str] = None

#Update Iqama Expiry Date
@router.put("/update-expiry-date")
async def update_expiry_date(data: ExpiryDateUpdateRequest):
    record = await OnboardedCustomer.get_or_none(iqama_id=data.iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")

    record.expiry_date = data.expiry_date
    if data.expiry_date_hijri:
        record.expiry_date_hijri = data.expiry_date_hijri

    record.updated_at = timezone.now()
    await record.save()

    return {"message": "Expiry date updated successfully"}

# ⬇️ PUT /customers/{iqama_id}
@router.put("/{iqama_id}")
async def update_customer(iqama_id: str, request: Request):
    record = await OnboardedCustomer.get_or_none(iqama_id=iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")

    device_id_header = request.headers.get('device_id')
    if record.device_id and device_id_header and record.device_id != device_id_header:
        raise HTTPException(status_code=403, detail="Onboarding has been resumed on another device. This session is no longer valid.")
        # ✅ Don't skip the update logic — allow update


    update_data = await request.json()
    updated_fields_list = []

    from re import sub

    def clean_amount(val):
        try:
            return float(sub(r'[^\d.]', '', val)) if val else None
        except:
            return None

    float_fields = [
    "salary_income", "business_income", "investment_income",
    "rental_income", "pension_income", "hafiz_income", "unemployed_income",
    "housewife_allowance", "student_allowance"
    ]

    for field, value in update_data.items():
        if hasattr(record, field):
            if field in float_fields:
                setattr(record, field, clean_amount(value))
            elif field == "mpin" and value:
                from utils.security import hash_mpin
                setattr(record, field, hash_mpin(value))

            elif field == "password" and value:
                from utils.security import hash_password
                setattr(record, field, hash_password(value))
            else:
                setattr(record, field, value)
            updated_fields_list.append(field)


    if not updated_fields_list:
        raise HTTPException(status_code=400, detail="No valid fields provided for update.")

    record.updated_at = timezone.now()
    await record.save()

    return {"message": "Customer record updated", "updated_fields": updated_fields_list}

# ⬇️ DELETE /customers/{iqama_id}
@router.delete("/{iqama_id}")
async def delete_customer(iqama_id: str):
    record = await OnboardedCustomer.get_or_none(iqama_id=iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer not found")

    await record.delete()
    return {"message": "Customer and associated device binding removed"}

# ⬇️ GET /customers/{iqama_id}/credentials  (safe: no plaintext)
@router.get("/{iqama_id}/credentials")
async def get_customer_credentials(iqama_id: str):
    """
    Returns non-sensitive credential info. Does NOT return plaintext password.
    """
    record = await OnboardedCustomer.get_or_none(iqama_id=iqama_id)
    if not record:
        raise HTTPException(status_code=404, detail="Customer record not found")

    # Indicate whether a password exists and when it was set
    return {
        "iqama_id": record.iqama_id,
        "password_set": bool(record.password),
        "password_is_hashed": bool(record.password and record.password.startswith("$")),  # crude hint for bcrypt/argon2
        "password_set_date": record.password_set_date,
        "password_set_time": record.password_set_time,
        "mpin_set_date": record.mpin_set_date,
        "mpin_set_time": record.mpin_set_time,
    }




