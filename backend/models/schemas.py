from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

class ResearchStartRequest(BaseModel):
    topic: str

class ResearchStatusResponse(BaseModel):
    id: str
    topic: str
    status: str
    created_at: datetime
    updated_at: datetime
    papers_count: int
    has_report: bool
    progress_percentage: int

    model_config = ConfigDict(from_attributes=True)

class ResearchDetailResponse(BaseModel):
    id: str
    topic: str
    status: str
    papers: Optional[List[Dict[str, Any]]] = None
    summaries: Optional[List[Dict[str, Any]]] = None
    criticism: Optional[str] = None
    gaps: Optional[Dict[str, Any]] = None
    roadmap: Optional[Dict[str, Any]] = None
    report_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
