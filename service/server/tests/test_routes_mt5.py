"""Tests for MT5 Gateway REST Endpoints."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from fastapi.testclient import TestClient
from routes import create_app
from mt5_gateway import get_mt5_gateway


class RouteMT5Tests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)
        self.gateway = get_mt5_gateway()

    def test_get_mt5_status(self):
        res = self.client.get("/v1/mt5/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["platform"], "MetaTrader 5")
        self.assertEqual(data["server"], self.gateway.server)
        self.assertEqual(data["login"], self.gateway.login)
        self.assertIn("connected", data)

    def test_get_mt5_risk(self):
        with patch.object(self.gateway, "check_ftmo_risk", return_value={
            "status": "SAFE",
            "can_trade": True,
            "daily_loss_pct": 0.5,
            "total_loss_pct": 1.2,
        }):
            res = self.client.get("/v1/mt5/risk")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "SAFE")
            self.assertTrue(data["can_trade"])

    def test_post_order_rejected_when_risk_breached(self):
        with patch.object(self.gateway, "place_order", return_value={
            "success": False,
            "error": "FTMO Risk Guard Tripped: Status BREACHED",
        }):
            res = self.client.post("/v1/mt5/order", json={
                "symbol": "XAUUSD",
                "side": "BUY",
                "volume": 0.1,
            })
            self.assertEqual(res.status_code, 400)
            self.assertIn("Risk Guard Tripped", res.json()["detail"])


if __name__ == "__main__":
    unittest.main()
