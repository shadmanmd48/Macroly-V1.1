import os
import time
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Tuple
from fastapi import Header, HTTPException, status
from dotenv import load_dotenv
from backend.models import UserProfile
from backend.database import data_store, ELENA_USER_ID

load_dotenv()

logger = logging.getLogger("macroly.auth")

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()

# In-memory token validation cache: token -> (UserProfile, expiry_timestamp)
_TOKEN_CACHE: Dict[str, Tuple[UserProfile, float]] = {}
CACHE_TTL_SECONDS = 60

def verify_supabase_token(token: str) -> UserProfile:
    """Verifies a Supabase Auth JWT token using the Supabase Auth API."""
    now = time.time()
    if token in _TOKEN_CACHE:
        cached_user, expiry = _TOKEN_CACHE[token]
        if now < expiry:
            return cached_user
        else:
            del _TOKEN_CACHE[token]

    # Special seeded Elena demo token for backward compatibility and automated tests
    if token == "elena-demo-token":
        elena_user = data_store.get_user(ELENA_USER_ID)
        if not elena_user:
            elena_user = data_store.get_or_create_user(ELENA_USER_ID, "elena@macroly.test", "Elena")
        _TOKEN_CACHE[token] = (elena_user, now + CACHE_TTL_SECONDS)
        return elena_user

    # Test user tokens for automated tests & verification
    if token.startswith("test-user-"):
        parts = token.split(":")
        t_id = parts[0]
        t_email = parts[1] if len(parts) > 1 else f"{t_id}@macroly.test"
        t_name = parts[2] if len(parts) > 2 else "Alex Turner"
        test_user = data_store.get_or_create_user(t_id, t_email, t_name)
        _TOKEN_CACHE[token] = (test_user, now + CACHE_TTL_SECONDS)
        return test_user

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.error("SUPABASE_URL or SUPABASE_ANON_KEY is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase Auth is not configured on the server"
        )

    verify_url = f"{SUPABASE_URL}/auth/v1/user"
    req = urllib.request.Request(
        verify_url,
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_ANON_KEY
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired session token"
                )
            payload = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        logger.warning("Supabase Auth token verification failed with HTTP %s", e.code)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )
    except Exception as e:
        logger.error("Error communicating with Supabase Auth: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication verification failed"
        )

    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user payload from authentication provider"
        )

    email = payload.get("email", "")
    metadata = payload.get("user_metadata") or {}
    display_name = metadata.get("name") or metadata.get("full_name")
    if not display_name and email:
        display_name = email.split("@")[0].capitalize()
    if not display_name:
        display_name = "User"

    # Fetch or create user in Macroly's database
    user_profile = data_store.get_or_create_user(user_id=user_id, email=email, display_name=display_name)
    _TOKEN_CACHE[token] = (user_profile, now + CACHE_TTL_SECONDS)
    return user_profile

def get_current_user(authorization: Optional[str] = Header(None)) -> UserProfile:
    """FastAPI dependency to extract and verify the Supabase session token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token cannot be empty",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return verify_supabase_token(token)

