#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, '/c/Users/ArT/pyprojects/Linap2')

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user import User
from app.models.video import Video
from app.models.map import Map
from app.core.settings.settings import settings

async def main():
    # Create async engine
    engine = create_async_engine(settings.database_url, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # Check users
        from sqlalchemy import select
        users = (await session.execute(select(User))).scalars().all()
        print(f"👥 Users in DB: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.email})")
        
        # Check videos
        videos = (await session.execute(select(Video))).scalars().all()
        print(f"\n🎥 Videos in DB: {len(videos)}")
        for video in videos:
            print(f"  - {video.title} (owner: {video.owner_id})")
        
        # Check maps
        maps = (await session.execute(select(Map))).scalars().all()
        print(f"\n🗺️ Maps in DB: {len(maps)}")
        for map_obj in maps:
            print(f"  - {map_obj.name}")
    
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())
