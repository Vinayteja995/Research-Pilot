import os
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


from backend.models.database import get_db, ResearchJob
from backend.models.schemas import ResearchStartRequest, ResearchStatusResponse, ResearchDetailResponse
from backend.workflows.research_graph import research_graph
from backend.services.pdf_service import PdfService
from backend.services.vector_service import VectorService

router = APIRouter(prefix="/api")

async def run_research_pipeline(job_id: str, topic: str, initial_papers: List[dict] = None):
    """
    Background worker that runs the LangGraph research graph and streams results to SQLite.
    """
    from backend.models.database import AsyncSessionLocal
    
    # Establish default state
    state = {
        "topic": topic,
        "job_id": job_id,
        "papers": initial_papers or [],
        "summaries": [],
        "criticism": "",
        "gaps": {},
        "roadmap": {},
        "report_markdown": "",
        "report_path": "",
        "status": "searching" if not initial_papers else "summarizing"
    }

    async with AsyncSessionLocal() as session:
        try:
            # Stream the LangGraph execution step-by-step
            async for event in research_graph.astream(state):
                for node_name, output in event.items():
                    print(f"--- Node Complete: {node_name} ---")
                    
                    # Update DB depending on which node has completed
                    db_update = {"status": output.get("status", "running")}
                    
                    if "papers" in output:
                        db_update["papers"] = output["papers"]
                    if "summaries" in output:
                        db_update["summaries"] = output["summaries"]
                    if "criticism" in output:
                        db_update["criticism"] = output["criticism"]
                    if "gaps" in output:
                        db_update["gaps"] = output["gaps"]
                    if "roadmap" in output:
                        db_update["roadmap"] = output["roadmap"]
                    if "report_markdown" in output:
                        db_update["report_markdown"] = output["report_markdown"]
                    if "report_path" in output:
                        db_update["report_path"] = output["report_path"]
                        
                    query = (
                        update(ResearchJob)
                        .where(ResearchJob.id == job_id)
                        .values(**db_update)
                    )
                    await session.execute(query)
                    await session.commit()
            
            # Finally set status to completed
            query = (
                update(ResearchJob)
                .where(ResearchJob.id == job_id)
                .values(status="completed")
            )
            await session.execute(query)
            await session.commit()
            print(f"--- RESEARCH JOB {job_id} COMPLETED SUCCESSFULLY ---")
            
        except Exception as e:
            print(f"ERROR: Research job {job_id} failed: {e}")
            query = (
                update(ResearchJob)
                .where(ResearchJob.id == job_id)
                .values(status="failed")
            )
            await session.execute(query)
            await session.commit()


@router.post("/research/start", response_model=Dict[str, str] if False else Any)
async def start_research(
    req: ResearchStartRequest, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    """
    Start research pipeline for a topic in a background task.
    """
    job_id = str(uuid.uuid4())
    
    new_job = ResearchJob(
        id=job_id,
        topic=req.topic,
        status="searching",
        papers=[],
        summaries=[],
        criticism="",
        gaps={},
        roadmap={}
    )
    
    db.add(new_job)
    await db.commit()
    
    # Start pipeline in the background
    background_tasks.add_task(run_research_pipeline, job_id, req.topic)
    
    return {"job_id": job_id, "status": "searching"}


@router.get("/research/status/{job_id}", response_model=ResearchStatusResponse)
async def get_research_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Check the current status and intermediate progress of a research job.
    """
    result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
        
    # Map status to progress percentage
    status_map = {
        "pending": 5,
        "searching": 15,
        "retrieving": 30,
        "summarizing": 50,
        "criticizing": 65,
        "gaps": 80,
        "roadmap": 90,
        "reporting": 95,
        "completed": 100,
        "failed": 100
    }
    progress = status_map.get(job.status, 0)
    papers_count = len(job.papers) if job.papers else 0
    has_report = bool(job.report_path and os.path.exists(job.report_path))
    
    return ResearchStatusResponse(
        id=job.id,
        topic=job.topic,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        papers_count=papers_count,
        has_report=has_report,
        progress_percentage=progress
    )


@router.get("/research/details/{job_id}", response_model=ResearchDetailResponse)
async def get_research_details(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get full research results (summaries, criticism, gaps, roadmap, report path) for a completed job.
    """
    result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Research job not found")
        
    return job


@router.get("/report/{job_id}")
async def get_report_pdf(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Serve the compiled PDF report for download.
    """
    result = await db.execute(select(ResearchJob).where(ResearchJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job or not job.report_path:
        raise HTTPException(status_code=404, detail="Report not generated yet or job not found")
        
    if not os.path.exists(job.report_path):
        raise HTTPException(status_code=404, detail="Compiled PDF file not found on disk")
        
    return FileResponse(
        path=job.report_path, 
        media_type="application/pdf", 
        filename=os.path.basename(job.report_path)
    )


@router.post("/upload")
async def upload_pdfs_and_research(
    background_tasks: BackgroundTasks,
    topic: str,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually upload paper PDFs, index them, and run research synthesis (summaries, critic, gaps, roadmap, report).
    """
    job_id = str(uuid.uuid4())
    pdf_service = PdfService()
    vector_service = VectorService()
    
    uploaded_papers = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            continue
            
        paper_id = f"manual_{uuid.uuid4().hex[:8]}"
        local_filename = f"{paper_id}.pdf"
        local_filepath = os.path.join(pdf_service.cache_dir, local_filename)
        
        # Save file to cache
        try:
            with open(local_filepath, "wb") as f:
                content = await file.read()
                f.write(content)
                
            # Extract plain text
            raw_text = pdf_service.extract_text_from_pdf(local_filepath)
            cleaned_text = pdf_service.clean_text(raw_text)
            
            title = file.filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
            
            # Index into vector database
            if cleaned_text:
                vector_service.add_paper_document(
                    paper_id=paper_id,
                    title=title,
                    text=cleaned_text
                )
                
                uploaded_papers.append({
                    "id": paper_id,
                    "title": title,
                    "authors": "Manually Uploaded Document",
                    "abstract": cleaned_text[:1000] + "...", # Store start of text as abstract
                    "url": "local-file",
                    "pdf_url": f"file:///{local_filepath}",
                    "published": ""
                })
        except Exception as e:
            print(f"Failed to process uploaded PDF {file.filename}: {e}")
            
    if not uploaded_papers:
        raise HTTPException(status_code=400, detail="No valid PDF documents were successfully uploaded and indexed.")
        
    # Create DB entry
    new_job = ResearchJob(
        id=job_id,
        topic=topic,
        status="summarizing",
        papers=uploaded_papers,
        summaries=[],
        criticism="",
        gaps={},
        roadmap={}
    )
    db.add(new_job)
    await db.commit()
    
    # Start the LangGraph workflow in the background starting from summarization
    background_tasks.add_task(run_research_pipeline, job_id, topic, uploaded_papers)
    
    return {"job_id": job_id, "status": "summarizing"}


@router.get("/research/jobs", response_model=List[ResearchStatusResponse])
async def list_research_jobs(db: AsyncSession = Depends(get_db)):
    """
    List all previously started or completed research jobs.
    """
    result = await db.execute(select(ResearchJob).order_by(ResearchJob.created_at.desc()))
    jobs = result.scalars().all()
    
    status_map = {
        "pending": 5,
        "searching": 15,
        "retrieving": 30,
        "summarizing": 50,
        "criticizing": 65,
        "gaps": 80,
        "roadmap": 90,
        "reporting": 95,
        "completed": 100,
        "failed": 100
    }
    
    response = []
    for job in jobs:
        progress = status_map.get(job.status, 0)
        papers_count = len(job.papers) if job.papers else 0
        has_report = bool(job.report_path and os.path.exists(job.report_path))
        
        response.append(
            ResearchStatusResponse(
                id=job.id,
                topic=job.topic,
                status=job.status,
                created_at=job.created_at,
                updated_at=job.updated_at,
                papers_count=papers_count,
                has_report=has_report,
                progress_percentage=progress
            )
        )
    return response
