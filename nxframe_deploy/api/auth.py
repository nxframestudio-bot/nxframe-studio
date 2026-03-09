"""NXFRAME STUDIO — Auth"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from api.database import get_db
from api.models.models import AdminSession
from api.config import settings

def verify_credentials(username: str, password: str) -> bool:
    return username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD

async def create_session(db: AsyncSession) -> str:
    token = secrets.token_urlsafe(64)
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
    db.add(AdminSession(token=token, expires_at=expires, is_active=True))
    await db.commit()
    return token

async def validate_session(token: str, db: AsyncSession) -> bool:
    if not token: return False
    result = await db.execute(
        select(AdminSession).where(
            AdminSession.token == token,
            AdminSession.is_active == True,
            AdminSession.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none() is not None

async def revoke_session(token: str, db: AsyncSession):
    result = await db.execute(select(AdminSession).where(AdminSession.token == token))
    s = result.scalar_one_or_none()
    if s: s.is_active = False; await db.commit()

async def cleanup_sessions(db: AsyncSession):
    await db.execute(delete(AdminSession).where(AdminSession.expires_at < datetime.now(timezone.utc)))
    await db.commit()

async def require_admin(
    admin_token: Optional[str] = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> bool:
    if not admin_token:
        raise HTTPException(status_code=401, detail="Login required.")
    if not await validate_session(admin_token, db):
        raise HTTPException(status_code=401, detail="Session expired.")
    return True
