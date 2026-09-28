"""
Firebase Authentication & RBAC Module for OPC AI Trader
Part of Lucky Trade OS

Super Admins:
- coach.chuyen@gmail.com (UID: i6C5uQ9lBnfCaekEPu68DPvK2QS2)
- tranngocchuyen1980@gmail.com (UID: bQXfjcvt3hYfhR1OYyQTC1UfbBF2)
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("firebase_auth")

SUPER_ADMIN_EMAILS = [
    email.strip().lower()
    for email in os.getenv("FIREBASE_SUPER_ADMIN_EMAILS", "coach.chuyen@gmail.com,tranngocchuyen1980@gmail.com").split(",")
    if email.strip()
]

SUPER_ADMIN_UIDS = [
    uid.strip()
    for uid in os.getenv("FIREBASE_SUPER_ADMIN_UIDS", "i6C5uQ9lBnfCaekEPu68DPvK2QS2,bQXfjcvt3hYfhR1OYyQTC1UfbBF2").split(",")
    if uid.strip()
]

_firebase_initialized = False

def init_firebase_admin():
    global _firebase_initialized
    if _firebase_initialized:
        return True

    try:
        import firebase_admin
        from firebase_admin import credentials

        # Check if already initialized in another module
        if len(firebase_admin._apps) > 0:
            _firebase_initialized = True
            return True

        cert_paths = [
            os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "opc-ai-trader-firebase-adminsdk-fbsvc-17705c7301.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "opc-ai-trader-firebase-adminsdk-fbsvc-17705c7301.json"),
            os.path.join(os.path.dirname(__file__), "opc-ai-trader-firebase-adminsdk-fbsvc-17705c7301.json"),
        ]

        cert_file = None
        for p in cert_paths:
            if os.path.exists(p):
                cert_file = p
                break

        if not cert_file:
            logger.warning("Firebase service account json not found in search paths: %s", cert_paths)
            return False

        cred = credentials.Certificate(cert_file)
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized successfully with cert: %s", cert_file)
        return True
    except Exception as exc:
        logger.error("Failed to initialize Firebase Admin SDK: %s", exc)
        return False


def verify_firebase_token(id_token: str) -> Optional[Dict[str, Any]]:
    """Verify Firebase ID token and return decoded token dict with RBAC roles."""
    if not init_firebase_admin():
        return None

    try:
        from firebase_admin import auth
        decoded = auth.verify_id_token(id_token)
        email = decoded.get("email", "").lower()
        uid = decoded.get("uid", "")

        is_super_admin = (email in SUPER_ADMIN_EMAILS) or (uid in SUPER_ADMIN_UIDS)
        decoded["is_super_admin"] = is_super_admin
        decoded["role"] = "SUPER_ADMIN" if is_super_admin else "TRADER"
        return decoded
    except Exception as exc:
        logger.warning("Firebase ID token verification failed: %s", exc)
        return None


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """FastAPI Dependency for authenticated Firebase users."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ")[1].strip()
    user = verify_firebase_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_super_admin(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """FastAPI Dependency strictly requiring Chairman / Super Admin role."""
    user = await get_current_user(authorization)
    if not user.get("is_super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin permission required (Reserved for Chairman Victor Chuyen)",
        )
    return user
