"""Creative Updates Router"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from pydantic import BaseModel
from api.database import get_db
from api.models.models import CreativeUpdate
from api.auth import require_admin

router = APIRouter(prefix="/api/updates", tags=["Updates"])

class UpdateCreate(BaseModel):
    title: str; category: str; summary: str
    source_url: Optional[str]=None; tags: Optional[str]=None; is_pinned: bool=False

class UpdateEdit(BaseModel):
    title: Optional[str]=None; category: Optional[str]=None; summary: Optional[str]=None
    source_url: Optional[str]=None; tags: Optional[str]=None; is_pinned: Optional[bool]=None

@router.get("", response_model=List[dict])
async def list_updates(category: Optional[str]=None, db: AsyncSession=Depends(get_db)):
    q = select(CreativeUpdate).order_by(CreativeUpdate.is_pinned.desc(), CreativeUpdate.created_at.desc())
    if category: q = q.where(CreativeUpdate.category==category)
    r = await db.execute(q)
    return [u.to_dict() for u in r.scalars().all()]

@router.post("", status_code=201)
async def create(payload: UpdateCreate, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    u = CreativeUpdate(**payload.model_dump())
    db.add(u); await db.commit(); await db.refresh(u)
    return u.to_dict()

@router.put("/{uid}")
async def edit(uid: int, payload: UpdateEdit, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(CreativeUpdate).where(CreativeUpdate.id==uid))
    u = r.scalar_one_or_none()
    if not u: raise HTTPException(404,"Not found.")
    for k,v in payload.model_dump(exclude_none=True).items(): setattr(u,k,v)
    await db.commit(); await db.refresh(u)
    return u.to_dict()

@router.delete("/{uid}", status_code=204)
async def delete(uid: int, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(CreativeUpdate).where(CreativeUpdate.id==uid))
    if not r.scalar_one_or_none(): raise HTTPException(404,"Not found.")
    await db.execute(sql_delete(CreativeUpdate).where(CreativeUpdate.id==uid)); await db.commit()
