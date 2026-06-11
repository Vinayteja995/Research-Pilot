import datetime
import json
from typing import AsyncGenerator
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Use local SQLite database by default
DATABASE_URL = "sqlite+aiosqlite:///./researchpilot.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

class ResearchJob(Base):
    __tablename__ = "research_jobs"

    id = Column(String, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, searching, retrieving, summarizing, criticizing, gaps, roadmap, reporting, completed, failed
    
    # Store dynamic workflow outputs as JSON or Text
    papers = Column(JSON, nullable=True)
    summaries = Column(JSON, nullable=True)
    criticism = Column(Text, nullable=True)
    gaps = Column(JSON, nullable=True)
    roadmap = Column(JSON, nullable=True)
    report_markdown = Column(Text, nullable=True)
    report_path = Column(String, nullable=True)
    
    # Audit timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
