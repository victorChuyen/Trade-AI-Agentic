"""Tests for MetaTrader 5 Gateway and FTMO Challenge Risk Rules."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import mt5_gateway
from mt5_gateway import MT5Gateway, get_mt5_gateway


class MT5GatewayTests(unittest.TestCase):
    def setUp(self):
        self.gateway = MT5Gateway(
            login=1514763831,
            password="36Ia$7Rh!",
            server="FTMO-Demo",
        )

    def test_gateway_initial_state(self):
        self.assertEqual(self.gateway.login, 1514763831)
        self.assertEqual(self.gateway.password, "36Ia$7Rh!")
        self.assertEqual(self.gateway.server, "FTMO-Demo")
        self.assertFalse(self.gateway.is_connected())

    def test_ftmo_risk_check_disconnected(self):
        result = self.gateway.check_ftmo_risk()
        self.assertEqual(result.get("status"), "UNKNOWN")

    def test_ftmo_risk_check_safe_state(self):
        with patch.object(self.gateway, "is_connected", return_value=True), \
             patch.object(self.gateway, "get_account_info", return_value={
                 "connected": True,
                 "balance": 100000.0,
                 "equity": 100500.0,
                 "profit": 500.0,
             }):
            self.gateway._initial_balance = 100000.0
            self.gateway._day_start_equity = 100000.0
            risk = self.gateway.check_ftmo_risk()

            self.assertEqual(risk["status"], "SAFE")
            self.assertTrue(risk["can_trade"])
            self.assertEqual(risk["daily_loss_pct"], 0.0)
            self.assertEqual(risk["total_loss_pct"], 0.0)

    def test_ftmo_risk_check_daily_loss_danger(self):
        with patch.object(self.gateway, "is_connected", return_value=True), \
             patch.object(self.gateway, "get_account_info", return_value={
                 "connected": True,
                 "balance": 100000.0,
                 "equity": 95400.0,  # 4.6% daily loss -> Danger threshold 4.5%
                 "profit": -4600.0,
             }):
            self.gateway._initial_balance = 100000.0
            self.gateway._day_start_equity = 100000.0
            risk = self.gateway.check_ftmo_risk()

            self.assertEqual(risk["status"], "DANGER")
            self.assertFalse(risk["can_trade"])
            self.assertEqual(risk["daily_loss_pct"], 4.6)

    def test_ftmo_risk_check_breached(self):
        with patch.object(self.gateway, "is_connected", return_value=True), \
             patch.object(self.gateway, "get_account_info", return_value={
                 "connected": True,
                 "balance": 100000.0,
                 "equity": 94800.0,  # 5.2% daily loss -> Breached!
                 "profit": -5200.0,
             }):
            self.gateway._initial_balance = 100000.0
            self.gateway._day_start_equity = 100000.0
            risk = self.gateway.check_ftmo_risk()

            self.assertEqual(risk["status"], "BREACHED")
            self.assertFalse(risk["can_trade"])
            self.assertGreaterEqual(risk["daily_loss_pct"], 5.0)

    def test_place_order_halted_when_risk_breached(self):
        with patch.object(self.gateway, "is_connected", return_value=True), \
             patch.object(self.gateway, "check_ftmo_risk", return_value={
                 "can_trade": False,
                 "status": "BREACHED",
             }):
            order = self.gateway.place_order("EURUSD", "BUY", 0.1)
            self.assertFalse(order["success"])
            self.assertIn("Trading Halted", order["error"])


if __name__ == "__main__":
    unittest.main()
