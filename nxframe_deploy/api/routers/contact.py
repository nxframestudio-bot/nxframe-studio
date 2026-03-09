"""Contact Router"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete, func
from pydantic import BaseModel, EmailStr
from api.database import get_db
from api.models.models import ContactMessage
from api.auth import require_admin
from api.email_service import notify_new_contact, send_autoreply

router = APIRouter(prefix="/api/contact", tags=["Contact"])

class ContactRequest(BaseModel):
    name: str; email: EmailStr; project_type: Optional[str]=None; message: str

@router.post("")
async def submit(payload: ContactRequest, db: AsyncSession=Depends(get_db)):
    if len(payload.message.strip())<10: raise HTTPException(400,"Message too short.")
    if len(payload.name.strip())<2: raise HTTPException(400,"Name too short.")
    msg = ContactMessage(name=payload.name.strip(), email=str(payload.email),
                         project_type=payload.project_type, message=payload.message.strip())
    db.add(msg); await db.commit()
    try:
        await notify_new_contact(payload.name, str(payload.email), payload.project_type or "", payload.message)
        await send_autoreply(payload.name, str(payload.email))
    except Exception as e: print(f"Email error: {e}")
    return {"success":True,"message":"Message sent! I'll get back to you within 24–48 hours."}

@router.get("/messages", response_model=List[dict])
async def get_msgs(unread_only: bool=Query(False), _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    q = select(ContactMessage).order_by(ContactMessage.created_at.desc())
    if unread_only: q = q.where(ContactMessage.is_read==False)
    r = await db.execute(q)
    return [m.to_dict() for m in r.scalars().all()]

@router.get("/unread-count")
async def unread(_: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(func.count()).select_from(ContactMessage).where(ContactMessage.is_read==False))
    return {"count": r.scalar()}

@router.put("/messages/{mid}/read")
async def mark_read(mid: int, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(ContactMessage).where(ContactMessage.id==mid))
    m = r.scalar_one_or_none()
    if not m: raise HTTPException(404,"Not found.")
    m.is_read=True; await db.commit()
    return {"success":True}

@router.delete("/messages/{mid}", status_code=204)
async def del_msg(mid: int, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(ContactMessage).where(ContactMessage.id==mid))
    if not r.scalar_one_or_none(): raise HTTPException(404,"Not found.")
    await db.execute(sql_delete(ContactMessage).where(ContactMessage.id==mid)); await db.commit()
