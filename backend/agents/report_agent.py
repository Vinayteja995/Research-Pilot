import json
from typing import Dict, Any
from backend.prompts.agent_prompts import REPORT_PROMPT
from backend.agents.base import call_gemini
from backend.services.report_service import ReportService

def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report Generator Agent Node.
    Consolidates summaries, critique, gaps, and roadmap into a single beautifully styled markdown paper, 
    and then invokes ReportService to compile a publication-grade PDF report.
    """
    topic = state.get("topic", "")
    summaries = state.get("summaries", [])
    criticism = state.get("criticism", "")
    gaps = state.get("gaps", {})
    roadmap = state.get("roadmap", {})
    job_id = state.get("job_id", "temp_job")
    
    print(f"--- REPORT GENERATOR AGENT: Compiling comprehensive report for '{topic}' ---")
    
    # Format data for prompt
    summaries_str = json.dumps(summaries, indent=2)
    gaps_str = json.dumps(gaps, indent=2)
    roadmap_str = json.dumps(roadmap, indent=2)
    
    prompt = REPORT_PROMPT.format(
        topic=topic,
        summaries_data=summaries_str,
        criticism_data=criticism,
        gaps_data=gaps_str,
        roadmap_data=roadmap_str
    )
    
    try:
        report_markdown = call_gemini(prompt=prompt)
    except Exception as e:
        print(f"Failed to generate Markdown report: {e}")
        report_markdown = f"# Literature Survey & Future Roadmap: {topic}\n\nFailed to compile full report."
        
    # Compile PDF
    print("Compiling PDF report...")
    report_service = ReportService()
    pdf_filename = f"ResearchPilot_Report_{job_id}.pdf"
    
    try:
        pdf_path = report_service.generate_pdf(report_markdown, pdf_filename)
    except Exception as e:
        print(f"Failed to compile PDF report: {e}")
        pdf_path = ""
        
    print("Report agent workflow complete.")
    return {
        "report_markdown": report_markdown,
        "report_path": pdf_path,
        "status": "completed"
    }
