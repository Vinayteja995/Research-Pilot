import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure project root is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

async def verify_system():
    print("==================================================")
    print("      RESEARCHPILOT BACKEND SYSTEM VERIFICATION    ")
    print("==================================================")
    
    # 1. Test imports
    print("\n[Step 1/4] Verifying imports...")
    try:
        from backend.models.database import Base, init_db, AsyncSessionLocal
        from backend.models.schemas import ResearchStartRequest, ResearchStatusResponse
        from backend.services.arxiv_service import ArxivService
        from backend.services.pdf_service import PdfService
        from backend.services.vector_service import VectorService
        from backend.services.report_service import ReportService
        from backend.workflows.research_graph import research_graph
        from backend.api.endpoints import router
        from backend.main import app
        
        print(" SUCCESS: All core modules, agents, services, and routes imported successfully!")
    except Exception as e:
        print(f" ERROR: Import failed: {e}")
        return False
        
    # 2. Test database setup
    print("\n[Step 2/4] Testing local SQLite DB initialization...")
    try:
        await init_db()
        print(" SUCCESS: SQLite DB created and schemas initialized successfully!")
    except Exception as e:
        print(f" ERROR: Database initialization failed: {e}")
        return False
        
    # 3. Test arXiv service connectivity (does not require Gemini API key)
    print("\n[Step 3/4] Testing arXiv API query parsing...")
    try:
        service = ArxivService()
        test_results = service.search_papers("Attention Is All You Need", max_results=1)
        if test_results:
            paper = test_results[0]
            print(f" SUCCESS: arXiv service connected and retrieved paper!")
            print(f"   - Title: {paper['title']}")
            print(f"   - Authors: {paper['authors']}")
            print(f"   - ID: {paper['id']}")
            print(f"   - PDF URL: {paper['pdf_url']}")
        else:
            print(" WARNING: arXiv search completed but returned no results. Check internet connection.")
    except Exception as e:
        print(f" ERROR: arXiv search failed: {e}")
        
    # 4. Check for GEMINI_API_KEY
    print("\n[Step 4/4] Checking Gemini API Environment...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print(" SUCCESS: GEMINI_API_KEY is configured in the environment.")
    else:
        print(" WARNING: GEMINI_API_KEY is not set. The multi-agent workflow will require this key to run successfully.")
        
    print("\n==================================================")
    print("             VERIFICATION COMPLETE                ")
    print("==================================================")
    return True

if __name__ == "__main__":
    asyncio.run(verify_system())
