"""Projects Router"""
import os, uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from pydantic import BaseModel
import aiofiles
from api.database import get_db
from api.models.models import Project
from api.auth import require_admin
from api.config import settings

router = APIRouter(prefix="/api/projects", tags=["Projects"])
CAT_ICONS  = {"graphic":"🎨","video":"🎬","3d":"🧊"}
CAT_LABELS = {"graphic":"Graphic Design","video":"Video Editing","3d":"3D Modeling"}

class ProjectCreate(BaseModel):
    title: str; category: str; description: Optional[str]=None; order: Optional[int]=0

class ProjectUpdate(BaseModel):
    title: Optional[str]=None; category: Optional[str]=None
    description: Optional[str]=None; is_visible: Optional[bool]=None; order: Optional[int]=None

class ReorderItem(BaseModel):
    id: int; order: int

def chk(cat):
    if cat not in CAT_ICONS: raise HTTPException(400, "Invalid category. Use: graphic, video, 3d")

async def save_img(file: UploadFile, pid: int) -> str:
    allowed = ["image/jpeg","image/png","image/webp","image/gif"]
    if file.content_type not in allowed: raise HTTPException(400, "Invalid image type.")
    data = await file.read()
    if len(data) > settings.max_bytes: raise HTTPException(400, f"Max {settings.MAX_FILE_SIZE_MB}MB.")
    ext = (file.filename or "img.jpg").rsplit(".",1)[-1].lower()
    fname = f"project_{pid}_{uuid.uuid4().hex[:8]}.{ext}"
    fpath = os.path.join(settings.UPLOAD_DIR, fname)
    async with aiofiles.open(fpath,"wb") as f: await f.write(data)
    try:
        with Image.open(fpath) as img:
            if img.width > 1200:
                h = int(img.height*(1200/img.width))
                img.resize((1200,h),Image.LANCZOS).save(fpath,optimize=True,quality=88)
    except: pass
    return f"/static/uploads/{fname}"

def del_file(url):
    if url and url.startswith("/static/uploads/"):
        p = "api" + url
        if os.path.exists(p): os.remove(p)

@router.get("", response_model=List[dict])
async def list_projects(category: Optional[str]=None, db: AsyncSession=Depends(get_db)):
    q = select(Project).where(Project.is_visible==True).order_by(Project.order, Project.id)
    if category: q = q.where(Project.category==category)
    r = await db.execute(q)
    return [p.to_dict() for p in r.scalars().all()]

@router.get("/all", response_model=List[dict])
async def list_all(_: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(Project).order_by(Project.order, Project.id))
    return [p.to_dict() for p in r.scalars().all()]

@router.post("", status_code=201)
async def create(payload: ProjectCreate, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    chk(payload.category)
    p = Project(title=payload.title, category=payload.category, label=CAT_LABELS[payload.category],
                description=payload.description, icon=CAT_ICONS[payload.category], order=payload.order or 0)
    db.add(p); await db.commit(); await db.refresh(p)
    return p.to_dict()

@router.put("/{pid}")
async def update(pid: int, payload: ProjectUpdate, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(Project).where(Project.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404,"Not found.")
    if payload.title       is not None: p.title       = payload.title
    if payload.description is not None: p.description = payload.description
    if payload.is_visible  is not None: p.is_visible  = payload.is_visible
    if payload.order       is not None: p.order       = payload.order
    if payload.category    is not None:
        chk(payload.category); p.category=payload.category
        p.label=CAT_LABELS[payload.category]; p.icon=CAT_ICONS[payload.category]
    await db.commit(); await db.refresh(p)
    return p.to_dict()

@router.post("/reorder")
async def reorder(items: List[ReorderItem], _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    for item in items:
        r = await db.execute(select(Project).where(Project.id==item.id))
        p = r.scalar_one_or_none()
        if p: p.order = item.order
    await db.commit()
    return {"success": True}

@router.delete("/{pid}", status_code=204)
async def delete(pid: int, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(Project).where(Project.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404,"Not found.")
    if p.image_url: del_file(p.image_url)
    await db.execute(sql_delete(Project).where(Project.id==pid)); await db.commit()

@router.post("/{pid}/image")
async def upload_img(pid: int, file: UploadFile=File(...), _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(Project).where(Project.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404,"Not found.")
    if p.image_url: del_file(p.image_url)
    p.image_url = await save_img(file, pid)
    await db.commit(); await db.refresh(p)
    return {"success":True,"image_url":p.image_url,"project":p.to_dict()}

@router.delete("/{pid}/image")
async def remove_img(pid: int, _: bool=Depends(require_admin), db: AsyncSession=Depends(get_db)):
    r = await db.execute(select(Project).where(Project.id==pid))
    p = r.scalar_one_or_none()
    if not p: raise HTTPException(404,"Not found.")
    if p.image_url: del_file(p.image_url); p.image_url=None; await db.commit()
    return {"success":True}
