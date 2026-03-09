"""Run once: python -m api.seed"""
import asyncio
from api.database import AsyncSessionLocal, init_db
from api.models.models import Project, CreativeUpdate
from sqlalchemy import select, func

PROJECTS = [
    {"title":"Product Visualization","category":"3d","label":"3D Modeling & Rendering","icon":"🧊","description":"High-fidelity product visualization with advanced 3D lighting and material design.","order":1},
    {"title":"Brand Identity","category":"graphic","label":"Graphic Design","icon":"🎨","description":"Complete brand identity system — logo, palette, typography, and guidelines.","order":2},
    {"title":"Cinematic Reel","category":"video","label":"Video Editing","icon":"🎬","description":"High-energy cinematic reel with colour grading and soundtrack sync.","order":3},
    {"title":"Environment Scene","category":"3d","label":"3D Modeling","icon":"🌐","description":"Fully detailed 3D environment with atmospheric lighting and post compositing.","order":4},
    {"title":"Social Campaign","category":"graphic","label":"Graphic Design","icon":"📱","description":"Multi-platform social media campaign with cohesive visual language.","order":5},
    {"title":"Motion Graphics","category":"video","label":"Video / Animation","icon":"✨","description":"Kinetic typography and motion graphics package for a product launch.","order":6},
]

UPDATES = [
    {"title":"AI-Generated 3D Textures Are Changing the Game","category":"trend","summary":"Tools like TripoSR and NVIDIA Instant NeRF let artists generate photo-real textures in seconds — reshaping how 3D artists handle material creation for product viz and environment design.","tags":"AI,3D,textures,workflow","is_pinned":True},
    {"title":"Bento Grid Layouts Dominating Brand Design","category":"trend","summary":"The bento grid aesthetic — segmented modular layouts inspired by Japanese lunch boxes — has exploded across brand identity, pitch decks, and social media. Perfect for showcasing multiple assets.","tags":"design,branding,layout","is_pinned":False},
    {"title":"DaVinci Resolve 19 — Key Updates for Video Editors","category":"tool","summary":"DaVinci Resolve 19 introduces AI-powered dialogue leveller, new colour warper, and IntelliTrack AI for automatic object tracking. Major upgrade for cinematic post-production workflows.","tags":"video,editing,DaVinci,tools","is_pinned":False},
    {"title":"Unreal Engine 5.4 Nanite for Film-Quality Real-Time 3D","category":"technique","summary":"UE5.4 Nanite Tessellation allows film-quality displacement maps in real-time — opening new doors for 3D visualization and virtual production. Rivals offline rendering paired with Lumen.","tags":"3D,UE5,realtime,technique","is_pinned":False},
    {"title":"Colour Grading Trend: Matte Teal & Orange is Back","category":"inspiration","summary":"The classic Hollywood teal-orange grade is back but refined — more subtle, paired with film grain overlays. Dominant in commercial reels and brand videos, especially lifestyle and fashion.","tags":"video,colour,grading,inspiration","is_pinned":False},
    {"title":"Blender 4.2 — Geometry Nodes Upgrade","category":"tool","summary":"Blender 4.2 brings redesigned Geometry Nodes with repeat zones, simulation node improvements, and new Material Slots node — making procedural workflows dramatically faster.","tags":"3D,Blender,tools,procedural","is_pinned":False},
]

async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        pc = (await db.execute(select(func.count()).select_from(Project))).scalar()
        if pc == 0:
            for d in PROJECTS: db.add(Project(**d))
            print(f"✅ Seeded {len(PROJECTS)} projects")
        else:
            print(f"⚠️  Projects already seeded ({pc}).")

        uc = (await db.execute(select(func.count()).select_from(CreativeUpdate))).scalar()
        if uc == 0:
            for d in UPDATES: db.add(CreativeUpdate(**d))
            print(f"✅ Seeded {len(UPDATES)} updates")
        else:
            print(f"⚠️  Updates already seeded ({uc}).")

        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed())
