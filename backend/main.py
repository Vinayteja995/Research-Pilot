# pyrefly: ignore [missing-import]
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from backend.models.database import init_db
from backend.api.endpoints import router as api_router

app = FastAPI(
    title="ResearchPilot API",
    description="Multi-Agent Autonomous Research Paper Assistant Backend Engine",
    version="1.0.0"
)

# Setup CORS for the Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify front-end domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    print("Starting up ResearchPilot Backend...")
    print("Initializing SQLite Database and creating tables...")
    await init_db()
    print("Database ready.")

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "ResearchPilot Core Agentic Engine",
        "version": "1.0.0"
    }

# Register the API routes
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
