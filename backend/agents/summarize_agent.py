import json
from typing import Dict, Any, List
from backend.prompts.agent_prompts import SUMMARIZATION_PROMPT
from backend.agents.base import call_gemini, parse_json_response

def summarize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarization Agent Node.
    Generates structured, academic-grade summaries for each paper in the state.
    """
    papers = state.get("papers", [])
    print(f"--- SUMMARIZATION AGENT: Creating summaries for {len(papers)} papers ---")
    
    summaries = []
    
    for paper in papers:
        paper_id = paper.get("id", "")
        title = paper.get("title", "")
        authors = paper.get("authors", "")
        abstract = paper.get("abstract", "")
        
        # If abstract is extremely short, use abstract or generic fallback
        if len(abstract) < 50:
            abstract = "Abstract not fully available from arXiv metadata. Refer to the full paper PDF text chunks."
            
        print(f"Summarizing paper: '{title}'...")
        
        prompt = SUMMARIZATION_PROMPT.format(
            paper_id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract
        )
        
        try:
            response_text = call_gemini(prompt=prompt, json_mode=True)
            summary_data = parse_json_response(response_text)
            summaries.append(summary_data)
        except Exception as e:
            print(f"Summarization failed for '{title}': {e}")
            # Fallback summary
            summaries.append({
                "paper_id": paper_id,
                "title": title,
                "objective": "Objective summary failed to generate.",
                "methodology": "Methodology summary failed to generate.",
                "findings": "Findings summary failed to generate.",
                "limitations": "Limitations summary failed to generate."
            })
            
    print(f"Created {len(summaries)} structured summaries.")
    return {
        "summaries": summaries,
        "status": "criticizing"
    }
