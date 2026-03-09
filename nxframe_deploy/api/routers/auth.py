"""Auth Router"""
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from api.database import get_db
from api.auth import verify_credentials, create_session, validate_session, revoke_session, cleanup_sessions
from api.config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    if not verify_credentials(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    await cleanup_sessions(db)
    token = await create_session(db)
    response.set_cookie(
        key="admin_token", value=token, httponly=True,
        secure=True, samesite="none",
        max_age=settings.SESSION_EXPIRE_HOURS * 3600, path="/",
    )
    return {"success": True}

@router.post("/logout")
async def logout(response: Response, admin_token: Optional[str] = Cookie(default=None), db: AsyncSession = Depends(get_db)):
    if admin_token:
        await revoke_session(admin_token, db)
    response.delete_cookie("admin_token", path="/", samesite="none", secure=True)
    return {"success": True}

@router.get("/status")
async def status(admin_token: Optional[str] = Cookie(default=None), db: AsyncSession = Depends(get_db)):
    valid = await validate_session(admin_token, db) if admin_token else False
    return {"authenticated": valid}
