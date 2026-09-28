"""
MetaTrader 5 & FTMO Challenge REST API Routes
Part of OPC AI Trader / Lucky Trade OS
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field

from mt5_gateway import get_mt5_gateway


class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Symbol name, e.g. XAUUSD, EURUSD, BTCUSD")
    side: str = Field(..., description="BUY or SELL")
    volume: float = Field(..., gt=0, description="Lot size, e.g. 0.01, 0.1, 1.0")
    sl: Optional[float] = Field(None, description="Stop loss price")
    tp: Optional[float] = Field(None, description="Take profit price")
    comment: Optional[str] = Field("OPC-AI", description="Order comment")


def register_mt5_routes(app: FastAPI) -> None:
    router = APIRouter(tags=["MetaTrader 5 / FTMO"])

    @router.get("/status")
    async def get_status():
        gateway = get_mt5_gateway()
        connected = gateway.is_connected()
        terminal_path = gateway.find_terminal_path()
        return {
            "platform": "MetaTrader 5",
            "server": gateway.server,
            "login": gateway.login,
            "connected": connected,
            "terminal_installed": terminal_path is not None,
            "terminal_path": terminal_path,
            "ftmo_account_mode": "Demo",
        }

    @router.post("/connect")
    async def connect():
        gateway = get_mt5_gateway()
        result = gateway.connect()
        return result

    @router.post("/disconnect")
    async def disconnect():
        gateway = get_mt5_gateway()
        gateway.disconnect()
        return {"success": True, "connected": False}

    @router.get("/account")
    async def get_account():
        gateway = get_mt5_gateway()
        return gateway.get_account_info()

    @router.get("/positions")
    async def get_positions():
        gateway = get_mt5_gateway()
        return {"positions": gateway.get_positions()}

    @router.get("/quote/{symbol}")
    async def get_quote(symbol: str):
        gateway = get_mt5_gateway()
        quote = gateway.get_quote(symbol.upper())
        if not quote:
            raise HTTPException(status_code=404, detail=f"No quote available for '{symbol}'")
        return quote

    @router.get("/risk")
    async def get_risk():
        gateway = get_mt5_gateway()
        return gateway.check_ftmo_risk()

    @router.post("/order")
    async def create_order(req: OrderRequest):
        gateway = get_mt5_gateway()
        result = gateway.place_order(
            symbol=req.symbol.upper(),
            side=req.side.upper(),
            volume=req.volume,
            sl=req.sl,
            tp=req.tp,
            comment=req.comment or "OPC-AI",
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Order failed"))
        return result

    @router.post("/close/{ticket}")
    async def close_order(ticket: int):
        gateway = get_mt5_gateway()
        result = gateway.close_position(ticket)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Close failed"))
        return result

    app.include_router(router, prefix="/v1/mt5")
    app.include_router(router, prefix="/api/mt5")
