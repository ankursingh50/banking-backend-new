# routes/transactions.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, time
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from tortoise.expressions import Q
from tortoise import Tortoise
from models.transaction_history import TransactionHistory


router = APIRouter(tags=["Transactions"])

# ---------- Schemas ----------
class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2

    transaction_id: int
    account_number: int
    transaction_type: Optional[str]
    transaction_date: date
    transaction_amount: Decimal
    available_balance: Optional[Decimal] = None
    time_of_transaction: Optional[time] = None
    merchant: Optional[str] = None
    reference_number: Optional[str] = None
    location_of_transaction: Optional[str] = None
    address: Optional[str] = None
    transaction_category: Optional[str] = None

class TransactionListOut(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[TransactionOut]

class DailySummaryOut(BaseModel):
    day: date
    txn_count: int
    total_amount: Decimal

# ---------- Endpoints ----------
@router.get("/transactions", response_model=TransactionListOut)
async def list_transactions(
    account_number: Optional[int] = Query(None, description="Filter by account_number"),
    from_date: Optional[date] = Query(None, description="Inclusive start date"),
    to_date: Optional[date] = Query(None, description="Inclusive end date"),
    merchant: Optional[str] = Query(None, description="Case-insensitive contains"),
    txn_type: Optional[str] = Query(None, description="Transaction type contains (ILIKE)"),
    reference_search: Optional[str] = Query(None, description="Search in reference number (ILIKE)"),
    txn_category: Optional[str] = Query(None, description="Transaction category contains (ILIKE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = Q()
    if account_number is not None:
        q &= Q(account_number=account_number)
    if from_date is not None:
        q &= Q(transaction_date__gte=from_date)
    if to_date is not None:
        q &= Q(transaction_date__lte=to_date)
    if merchant:
        q &= Q(merchant__icontains=merchant)
    if txn_type:
        q &= Q(transaction_type__icontains=txn_type)
    if reference_search:
        q &= Q(reference_number__icontains=reference_search)
    if txn_category:  # ✅ add this
        q &= Q(transaction_category__icontains=txn_category)

    total = await TransactionHistory.filter(q).count()
    rows = (
        await TransactionHistory
        .filter(q)
        .order_by("-transaction_date", "-time_of_transaction")
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = [TransactionOut.model_validate(r) for r in rows]
    return TransactionListOut(total=total, limit=limit, offset=offset, items=items)


@router.get("/transactions/{transaction_id}", response_model=TransactionOut)
async def get_transaction(transaction_id: int):
    row = await TransactionHistory.get_or_none(transaction_id=transaction_id)
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionOut.model_validate(row)


@router.get("/accounts/{account_number}/transactions/daily-summary",
            response_model=List[DailySummaryOut])
async def account_daily_summary(
    account_number: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
):
    # Pure SQL for clarity (quotes needed for spaced column names)
    sql = """
        SELECT "Transaction Date" AS day,
               COUNT(*) AS txn_count,
               SUM("Transaction amount") AS total_amount
        FROM transaction_history
        WHERE account_number = $1
          {from_clause}
          {to_clause}
        GROUP BY day
        ORDER BY day DESC
    """
    params: List = [account_number]
    from_clause = ""
    to_clause = ""

    if from_date:
        from_clause = "AND \"Transaction Date\" >= $2"
        params.append(from_date)
    if to_date:
        # if both provided, to_date becomes $3; otherwise $2
        to_clause = f"AND \"Transaction Date\" <= ${len(params)+1}"
        params.append(to_date)

    sql = sql.format(from_clause=from_clause, to_clause=to_clause)
    rows = await Tortoise.get_connection("default").execute_query_dict(sql, params)
    return [DailySummaryOut(**r) for r in rows]
