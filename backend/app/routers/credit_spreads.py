from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from datetime import date

from ..services.credit_spreads import AccountSettings, Ticket, CloseRequest, get_credit_spreads

router = APIRouter(prefix="/credit-spreads", tags=["credit-spread-paper"])


@router.get("/dashboard")
def dashboard():
    return get_credit_spreads().dashboard()


@router.get("/market")
def market(expiry: date | None = None):
    return get_credit_spreads().market(expiry.isoformat() if expiry else None)


@router.get("/chart")
def chart(interval: str = "1hour"):
    try:
        return get_credit_spreads().chart(interval)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, "Candle data is unavailable; retained trading records are unaffected.") from exc


@router.post("/preview")
def preview(ticket: Ticket):
    return get_credit_spreads().preview(ticket)


@router.post("/orders")
def enter(ticket: Ticket):
    return get_credit_spreads().enter(ticket)


@router.post("/trades/{trade_id}/close")
def close(trade_id: str, request: CloseRequest):
    try:
        return get_credit_spreads().close(trade_id, request)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/trades/{trade_id}/marks")
def marks(trade_id: str):
    return get_credit_spreads().marks(trade_id)


@router.put("/settings")
def settings(value: AccountSettings):
    try:
        return get_credit_spreads().settings(value)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/export")
def export(kind: str = Query("trades", pattern="^(trades|orders)$")):
    return Response(get_credit_spreads().export(kind), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="nifty-credit-spread-{kind}.csv"'})
