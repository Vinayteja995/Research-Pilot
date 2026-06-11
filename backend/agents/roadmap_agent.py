import json
from typing import Dict, Any
from backend.prompts.agent_prompts import ROADMAP_PROMPT
from backend.agents.base import call_gemini, parse_json_response

def roadmap_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Roadmap Agent Node.
    Creates a highly structured Beginner -> Intermediate -> Advanced syllabus for mastering the researched topic.
    """
    topic = state.get("topic", "")
    print(f"--- ROADMAP AGENT: Building technical syllabus for '{topic}' ---")
    
    prompt = ROADMAP_PROMPT.format(topic=topic)
    
    try:
        response_text = call_gemini(prompt=prompt, json_mode=True)
        roadmap_data = parse_json_response(response_text)
    except Exception as e:
        print(f"Roadmap generation failed: {e}")
        roadmap_data = {
            "beginner": {
                "concepts": [f"Foundations of {topic}"],
                "reading": ["Introductory textbooks and review papers on arXiv."],
                "projects": ["Build a simple basic model reproducing basic concepts."]
            },
            "intermediate": {
                "concepts": [f"Advanced architectures in {topic}"],
                "reading": ["Key highly-cited arXiv papers in state.get('papers') list."],
                "projects": ["Replicate a major paper's experimental findings using standard frameworks."]
            },
            "advanced": {
                "concepts": [f"Cutting edge and unresolved research topics"],
                "reading": ["Active research preprints on arXiv."],
                "projects": ["Select one of the identified research gaps and propose a detailed design."]
            }
        }
        
    print("Completed technical syllabus generation.")
    return {
        "roadmap": roadmap_data,
        "status": "reporting"
    }
