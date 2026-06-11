import json
from typing import Dict, Any
from backend.prompts.agent_prompts import GAP_PROMPT
from backend.agents.base import call_gemini, parse_json_response

def gap_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research Gap Agent Node.
    Analyzes summaries and criticism to formulate 3-5 structured research gaps and open problems.
    """
    topic = state.get("topic", "")
    summaries = state.get("summaries", [])
    criticism = state.get("criticism", "")
    
    print(f"--- RESEARCH GAP AGENT: Identifying gaps for '{topic}' ---")
    
    # Serialize summaries
    serialized_summaries = []
    for idx, s in enumerate(summaries):
        serialized_summaries.append(f"- Paper #{idx+1} '{s.get('title')}': {s.get('objective')}")
    summaries_data = "\n".join(serialized_summaries)
    
    prompt = GAP_PROMPT.format(
        topic=topic,
        summaries_data=summaries_data,
        criticism_data=criticism
    )
    
    try:
        response_text = call_gemini(prompt=prompt, json_mode=True)
        gaps_data = parse_json_response(response_text)
    except Exception as e:
        print(f"Research gap generation failed: {e}")
        gaps_data = {
            "gaps": [
                {
                    "title": "Scalability & Real-World Deployability Gaps",
                    "description": "Most existing literature focuses on theoretical, small-scale evaluations rather than production setups.",
                    "implications": "Prevents translation of theoretical innovations into industry value.",
                    "proposed_approach": "Develop comprehensive benchmarks comparing model architectures in low-latency settings."
                }
            ]
        }
        
    print(f"Identified {len(gaps_data.get('gaps', []))} research gaps.")
    return {
        "gaps": gaps_data,
        "status": "roadmap"
    }
