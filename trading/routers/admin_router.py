"""
Admin-only JSON endpoints for the mobile/web app.

Currently exposes invite-code management. Guarded by the existing `is_admin`
flag on users; both Bearer JWT and session-cookie auth are accepted via
`get_current_user`.
"""
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth.jwt_tokens import get_current_user
from utils import database

logger = logging.getLogger("routers.admin")
router = APIRouter(prefix="/v1/admin", tags=["admin"])


def _require_admin(user: dict) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "admin_required")
    return user


# ==================== Schemas ====================

class InviteCreateBody(BaseModel):
    code: str | None = None  # auto-generated when omitted
    max_uses: int = 1  # 0 = unlimited
    expires_at: str | None = None  # ISO timestamp; null = never
    note: str | None = None


class InviteRow(BaseModel):
    code: str
    created_by_user_id: int | None = None
    max_uses: int
    used_count: int
    expires_at: str | None = None
    note: str | None = None
    created_at: str


class InviteListResponse(BaseModel):
    invites: list[InviteRow]


class InviteRedemptionRow(BaseModel):
    code: str
    user_id: int
    redeemed_at: str


# ==================== Routes ====================

@router.post("/invites", response_model=InviteRow, status_code=status.HTTP_201_CREATED)
def create_invite(body: InviteCreateBody, user: dict = Depends(get_current_user)):
    _require_admin(user)
    if body.max_uses < 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "max_uses must be >= 0")
    try:
        row = database.create_invite_code(
            created_by_user_id=user["id"],
            max_uses=body.max_uses,
            expires_at=body.expires_at,
            note=body.note,
            code=body.code,
        )
    except Exception as e:
        logger.warning(f"create_invite failed: {e}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return row


@router.get("/invites", response_model=InviteListResponse)
def list_invites(user: dict = Depends(get_current_user), limit: int = 200):
    _require_admin(user)
    return InviteListResponse(invites=database.list_invite_codes(limit=limit))


@router.delete("/invites/{code}")
def delete_invite(code: str, user: dict = Depends(get_current_user)):
    _require_admin(user)
    n = database.delete_invite_code(code)
    if n == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invite_not_found")
    return {"deleted": n}


@router.get("/invites/{code}/redemptions", response_model=list[InviteRedemptionRow])
def get_redemptions(code: str, user: dict = Depends(get_current_user)):
    _require_admin(user)
    if not database.get_invite_code(code):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invite_not_found")
    return database.list_invite_redemptions(code)


@router.get("/egress-ip")
def egress_ip(user: dict = Depends(get_current_user)):
    """Report this server's outbound IP — needed for OKX API IP whitelisting."""
    _require_admin(user)
    results: dict[str, str | None] = {}
    for name, url in [
        ("ifconfig.me", "https://ifconfig.me/ip"),
        ("ipify", "https://api.ipify.org"),
        ("icanhazip", "https://icanhazip.com"),
    ]:
        try:
            r = httpx.get(url, timeout=5.0)
            results[name] = r.text.strip()
        except Exception as e:
            results[name] = f"error: {e}"
    return {"egress_ips": results}
