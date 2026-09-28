"""
OPC AI Trader / Lucky Trade OS — MetaTrader 5 Gateway
Dedicated Gateway for MetaTrader 5 & FTMO Challenge Accounts

Leadership: Chairman Victor Chuyen & AI CEO Lucky
Configured for FTMO Account:
- Server: FTMO-Demo
- Login: 1514763831
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("mt5_gateway")

try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

# Default FTMO Credentials (can be overridden via environment variables)
DEFAULT_FTMO_LOGIN = int(os.getenv("LUCKY_MT5_LOGIN", "1514763831"))
DEFAULT_FTMO_PASSWORD = os.getenv("LUCKY_MT5_PASSWORD", "36Ia$7Rh!")
DEFAULT_FTMO_INVESTOR_PW = os.getenv("LUCKY_MT5_INVESTOR_PASSWORD", "!6Qhf?*XV9@JK")
DEFAULT_FTMO_SERVER = os.getenv("LUCKY_MT5_SERVER", "FTMO-Demo")
DEFAULT_MAGIC_NUMBER = int(os.getenv("LUCKY_MT5_MAGIC", "202688"))

# FTMO Prop Firm Risk Limits
FTMO_MAX_DAILY_LOSS_PCT = float(os.getenv("FTMO_MAX_DAILY_LOSS_PCT", "5.0"))
FTMO_MAX_TOTAL_LOSS_PCT = float(os.getenv("FTMO_MAX_TOTAL_LOSS_PCT", "10.0"))
FTMO_SAFETY_TRIGGER_DAILY_PCT = float(os.getenv("FTMO_SAFETY_TRIGGER_DAILY_PCT", "4.5"))
FTMO_SAFETY_TRIGGER_TOTAL_PCT = float(os.getenv("FTMO_SAFETY_TRIGGER_TOTAL_PCT", "9.0"))

STANDARD_MT5_SEARCH_PATHS = [
    r"C:\Program Files\MetaTrader 5\terminal64.exe",
    r"C:\Program Files\FTMO MetaTrader 5\terminal64.exe",
    r"C:\Program Files\FTMO Global Markets MetaTrader 5\terminal64.exe",
    r"C:\Program Files\ICMarkets MetaTrader 5\terminal64.exe",
    r"C:\Program Files\Exness MetaTrader 5\terminal64.exe",
    r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
    r"C:\Program Files (x86)\FTMO MetaTrader 5\terminal64.exe",
    os.path.expanduser(r"~\AppData\Local\Programs\MetaTrader 5\terminal64.exe"),
]


class MT5Gateway:
    """Enterprise MT5 Gateway for live trading, quotes, and FTMO risk management."""

    def __init__(
        self,
        login: int = DEFAULT_FTMO_LOGIN,
        password: str = DEFAULT_FTMO_PASSWORD,
        server: str = DEFAULT_FTMO_SERVER,
        path: Optional[str] = None,
    ):
        self.login = login
        self.password = password
        self.server = server
        self.custom_path = path or os.getenv("LUCKY_MT5_PATH")
        self._connected = False
        self._last_error = None
        self._initial_balance = None
        self._day_start_equity = None
        self._day_start_date = None

    def find_terminal_path(self) -> Optional[str]:
        """Locate the terminal64.exe on the local machine."""
        if self.custom_path and os.path.exists(self.custom_path):
            return self.custom_path
        for candidate in STANDARD_MT5_SEARCH_PATHS:
            if os.path.exists(candidate):
                return candidate
        return None

    def connect(self) -> Dict[str, Any]:
        """Initialize connection to MetaTrader 5 and authenticate account."""
        if mt5 is None:
            self._connected = False
            self._last_error = "MetaTrader5 Python package not available"
            return {
                "success": False,
                "error": self._last_error,
                "hint": "Run `uv pip install metatrader5` in Python 3.11 environment.",
            }

        terminal_path = self.find_terminal_path()
        try:
            # Step 1: Connect directly to running MT5 terminal instance (instant, no scan hang)
            initialized = mt5.initialize()
            if not initialized and terminal_path:
                initialized = mt5.initialize(path=terminal_path)

            if not initialized:
                error_code, error_msg = mt5.last_error()
                self._connected = False
                self._last_error = f"MT5 Init Failed ({error_code}): {error_msg}"
                logger.warning("MT5 Init Failed: %s", self._last_error)
                return {
                    "success": False,
                    "connected": False,
                    "error": self._last_error,
                    "terminal_path": terminal_path,
                    "installed": terminal_path is not None,
                    "hint": "Ensure MetaTrader 5 terminal is open on the machine.",
                }

            # Step 2: Check active account in terminal
            current_acc = mt5.account_info()
            if current_acc and self.login and current_acc.login != int(self.login):
                # Attempt to switch to target account
                login_kwargs = {"login": int(self.login)}
                if self.password:
                    login_kwargs["password"] = self.password
                if self.server:
                    login_kwargs["server"] = self.server
                logged_in = mt5.login(**login_kwargs)
                if not logged_in:
                    logger.info(
                        "Target account #%s on %s not active, using current terminal account #%s (%s)",
                        self.login,
                        self.server,
                        current_acc.login,
                        current_acc.server,
                    )

            self._connected = True
            self._last_error = None
            account = self.get_account_info()
            logger.info("MT5 Connected: Account #%s on %s | Balance: %s", account.get("login"), account.get("server"), account.get("balance"))
            return {
                "success": True,
                "connected": True,
                "account": account,
            }
        except Exception as exc:
            self._connected = False
            self._last_error = str(exc)
            logger.exception("MT5 connection exception: %s", exc)
            return {
                "success": False,
                "connected": False,
                "error": str(exc),
            }

    def disconnect(self) -> None:
        """Disconnect and shutdown MT5 IPC connection."""
        if mt5 and self._connected:
            try:
                mt5.shutdown()
            except Exception:
                pass
        self._connected = False

    def is_connected(self) -> bool:
        """Check if connection is currently active."""
        if mt5 is None:
            return False
        acc = mt5.account_info()
        if acc is not None and getattr(acc, 'login', 0) > 0:
            self._connected = True
            return True
        if self._connected:
            info = mt5.terminal_info()
            return info is not None and info.connected
        return False

    def get_account_info(self) -> Dict[str, Any]:
        """Fetch real-time account parameters (Balance, Equity, Profit, Margin)."""
        if not self.is_connected():
            return {
                "connected": False,
                "login": self.login,
                "server": self.server,
                "error": self._last_error or "Not connected to MT5",
            }
        info = mt5.account_info()
        if not info:
            return {"connected": False, "error": "Unable to fetch account info"}

        acc_dict = info._asdict()
        # Initialize baseline for daily loss tracking
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._day_start_date != today_str:
            self._day_start_date = today_str
            self._day_start_equity = acc_dict.get("equity")
            if self._initial_balance is None:
                self._initial_balance = acc_dict.get("balance")

        return {
            "connected": True,
            "login": acc_dict.get("login"),
            "trade_mode": "Demo" if acc_dict.get("trade_mode") == 0 else "Live",
            "name": acc_dict.get("name"),
            "server": acc_dict.get("server"),
            "currency": acc_dict.get("currency"),
            "leverage": acc_dict.get("leverage"),
            "balance": acc_dict.get("balance"),
            "equity": acc_dict.get("equity"),
            "profit": acc_dict.get("profit"),
            "margin": acc_dict.get("margin"),
            "margin_free": acc_dict.get("margin_free"),
            "margin_level": acc_dict.get("margin_level"),
            "time": datetime.now(timezone.utc).isoformat(),
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        """Fetch all currently open positions."""
        if not self.is_connected():
            return []
        positions = mt5.positions_get()
        if positions is None:
            return []
        result = []
        for p in positions:
            p_dict = p._asdict()
            p_dict["side"] = "BUY" if p_dict.get("type") == 0 else "SELL"
            p_dict["time_iso"] = datetime.fromtimestamp(p_dict.get("time", 0), tz=timezone.utc).isoformat()
            result.append(p_dict)
        return result

    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current tick price for any symbol (e.g. XAUUSD, BTCUSD, EURUSD)."""
        if not self.is_connected():
            return None
        # Ensure symbol is selected in Market Watch
        mt5.symbol_select(symbol, True)
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return None
        info = mt5.symbol_info(symbol)
        spread = info.spread if info else 0
        digits = info.digits if info else 2
        return {
            "symbol": symbol,
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "spread": spread,
            "digits": digits,
            "time": datetime.fromtimestamp(tick.time, tz=timezone.utc).isoformat(),
        }

    def check_ftmo_risk(self) -> Dict[str, Any]:
        """Evaluate current metrics against strict FTMO Challenge Drawdown Rules."""
        acc = self.get_account_info()
        if not acc.get("connected"):
            return {"status": "UNKNOWN", "reason": "MT5 not connected"}

        equity = acc.get("equity", 0.0)
        balance = acc.get("balance", 0.0)
        initial_balance = self._initial_balance or balance
        day_start = self._day_start_equity or initial_balance

        # 1. Daily Loss Check (Relative to day start equity)
        daily_loss_amount = max(0.0, day_start - equity)
        daily_loss_pct = (daily_loss_amount / day_start * 100.0) if day_start > 0 else 0.0

        # 2. Total Loss Check (Relative to initial balance)
        total_loss_amount = max(0.0, initial_balance - equity)
        total_loss_pct = (total_loss_amount / initial_balance * 100.0) if initial_balance > 0 else 0.0

        is_daily_breached = daily_loss_pct >= FTMO_MAX_DAILY_LOSS_PCT
        is_total_breached = total_loss_pct >= FTMO_MAX_TOTAL_LOSS_PCT
        is_danger = (
            daily_loss_pct >= FTMO_SAFETY_TRIGGER_DAILY_PCT or total_loss_pct >= FTMO_SAFETY_TRIGGER_TOTAL_PCT
        )

        status = "SAFE"
        if is_daily_breached or is_total_breached:
            status = "BREACHED"
        elif is_danger:
            status = "DANGER"
        elif daily_loss_pct >= 2.0 or total_loss_pct >= 4.0:
            status = "WARNING"

        return {
            "status": status,
            "initial_balance": initial_balance,
            "day_start_equity": day_start,
            "current_equity": equity,
            "current_balance": balance,
            "daily_loss_amount": round(daily_loss_amount, 2),
            "daily_loss_pct": round(daily_loss_pct, 2),
            "daily_loss_limit_pct": FTMO_MAX_DAILY_LOSS_PCT,
            "total_loss_amount": round(total_loss_amount, 2),
            "total_loss_pct": round(total_loss_pct, 2),
            "total_loss_limit_pct": FTMO_MAX_TOTAL_LOSS_PCT,
            "can_trade": status not in {"BREACHED", "DANGER"},
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

    def place_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "OPC-AI",
    ) -> Dict[str, Any]:
        """Send execution order to MT5 with risk gate enforcement."""
        if not self.is_connected():
            return {"success": False, "error": "Not connected to MT5"}

        # Enforce Gate 2: FTMO Risk Guard
        risk = self.check_ftmo_risk()
        if not risk.get("can_trade"):
            return {
                "success": False,
                "error": f"FTMO Risk Guard Tripped: Status {risk.get('status')}. Trading Halted!",
                "risk": risk,
            }

        mt5.symbol_select(symbol, True)
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return {"success": False, "error": f"Symbol '{symbol}' not found on FTMO server"}

        quote = self.get_quote(symbol)
        if not quote:
            return {"success": False, "error": f"No tick available for symbol '{symbol}'"}

        is_buy = side.strip().upper() in {"BUY", "LONG"}
        price = quote["ask"] if is_buy else quote["bid"]
        order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": order_type,
            "price": price,
            "deviation": 20,
            "magic": DEFAULT_MAGIC_NUMBER,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        if sl is not None:
            request["sl"] = float(sl)
        if tp is not None:
            request["tp"] = float(tp)

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            retcode = getattr(result, "retcode", None)
            comment_res = getattr(result, "comment", mt5.last_error())
            return {
                "success": False,
                "retcode": retcode,
                "error": f"Order rejected: {comment_res}",
                "request": request,
            }

        return {
            "success": True,
            "ticket": result.order,
            "volume": result.volume,
            "price": result.price,
            "comment": result.comment,
            "time": datetime.now(timezone.utc).isoformat(),
        }

    def close_position(self, ticket: int) -> Dict[str, Any]:
        """Close an existing open position by ticket ID."""
        if not self.is_connected():
            return {"success": False, "error": "Not connected to MT5"}

        positions = mt5.positions_get(ticket=int(ticket))
        if not positions or len(positions) == 0:
            return {"success": False, "error": f"Position #{ticket} not found"}

        pos = positions[0]
        symbol = pos.symbol
        volume = pos.volume
        pos_type = pos.type

        # Reverse side to close
        close_type = mt5.ORDER_TYPE_SELL if pos_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        quote = self.get_quote(symbol)
        if not quote:
            return {"success": False, "error": f"No quote for closing {symbol}"}
        price = quote["bid"] if close_type == mt5.ORDER_TYPE_SELL else quote["ask"]

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": int(ticket),
            "symbol": symbol,
            "volume": float(volume),
            "type": close_type,
            "price": price,
            "deviation": 20,
            "magic": DEFAULT_MAGIC_NUMBER,
            "comment": "OPC-AI-Close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            return {
                "success": False,
                "error": f"Close failed: {getattr(result, 'comment', mt5.last_error())}",
            }

        return {
            "success": True,
            "ticket": ticket,
            "closed_price": result.price,
            "time": datetime.now(timezone.utc).isoformat(),
        }


# Singleton Global Gateway Instance
_global_mt5_gateway: Optional[MT5Gateway] = None


def get_mt5_gateway() -> MT5Gateway:
    global _global_mt5_gateway
    if _global_mt5_gateway is None:
        _global_mt5_gateway = MT5Gateway()
    return _global_mt5_gateway
