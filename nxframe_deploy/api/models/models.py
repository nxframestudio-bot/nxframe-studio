"""NXFRAME STUDIO — DB Models"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func
from api.database import Base

class Project(Base):
    __tablename__ = "projects"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    category    = Column(String(50), nullable=False)
    label       = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon        = Column(String(10), default="🎨")
    image_url   = Column(String(500), nullable=True)
    order       = Column(Integer, default=0)
    is_visible  = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "category": self.category,
            "label": self.label, "description": self.description, "icon": self.icon,
            "image_url": self.image_url, "order": self.order, "is_visible": self.is_visible,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(150), nullable=False)
    email        = Column(String(255), nullable=False)
    project_type = Column(String(150), nullable=True)
    message      = Column(Text, nullable=False)
    is_read      = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email,
            "project_type": self.project_type, "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class AdminSession(Base):
    __tablename__ = "admin_sessions"
    id         = Column(Integer, primary_key=True, index=True)
    token      = Column(String(512), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active  = Column(Boolean, default=True)

class CreativeUpdate(Base):
    __tablename__ = "creative_updates"
    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String(300), nullable=False)
    category   = Column(String(100), nullable=False)
    summary    = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    tags       = Column(String(500), nullable=True)
    is_pinned  = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "category": self.category,
            "summary": self.summary, "source_url": self.source_url,
            "tags": self.tags.split(",") if self.tags else [],
            "is_pinned": self.is_pinned,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
