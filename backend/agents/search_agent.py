from typing import Dict, Any
from backend.prompts.agent_prompts import SEARCH_QUERY_PROMPT
from backend.services.arxiv_service import ArxivService
from backend.agents.base import call_gemini, parse_json_response

def search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search Agent Node.
    Generates search queries for the research topic, queries arXiv, and populates the papers in state.
    """
    topic = state.get("topic", "")
    print(f"--- SEARCH AGENT: Formulating queries for '{topic}' ---")
    
    # Generate search queries
    prompt = SEARCH_QUERY_PROMPT.format(topic=topic)
    try:
        response_text = call_gemini(prompt=prompt, json_mode=True)
        query_data = parse_json_response(response_text)
        queries = query_data.get("queries", [topic])
    except Exception as e:
        print(f"Search query generation failed: {e}. Using raw topic as query.")
        queries = [topic]

    print(f"Generated queries: {queries}")
    
    arxiv_service = ArxivService()
    all_papers = {}
    
    # Query arXiv for each generated query
    for query in queries:
        print(f"Searching arXiv for: '{query}'...")
        results = arxiv_service.search_papers(query, max_results=3)
        for paper in results:
            # Prevent duplicate papers by using ID as unique key
            all_papers[paper["id"]] = paper
            
    papers_list = list(all_papers.values())
    print(f"Found {len(papers_list)} unique papers on arXiv.")
    
    return {
        "papers": papers_list,
        "status": "retrieving"
    }
