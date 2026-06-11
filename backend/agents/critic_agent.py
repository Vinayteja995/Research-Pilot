import json
from typing import Dict, Any
from backend.prompts.agent_prompts import CRITIC_PROMPT
from backend.agents.base import call_gemini

def critic_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Critic Agent Node.
    Synthesizes multiple papers, analyzing agreements, disagreements, weaknesses, and levels of empirical evidence.
    """
    topic = state.get("topic", "")
    summaries = state.get("summaries", [])
    
    print(f"--- CRITIC AGENT: Synthesizing critique for '{topic}' across {len(summaries)} papers ---")
    
    if not summaries:
        print("No paper summaries available for critique. Generating generic review.")
        return {
            "criticism": "No papers were retrieved and summarized for the topic.",
            "status": "gaps"
        }
        
    # Serialize summaries for prompt
    serialized_summaries = []
    for idx, s in enumerate(summaries):
        serialized_summaries.append(
            f"Paper #{idx+1}: {s.get('title')}\n"
            f"- Objective: {s.get('objective')}\n"
            f"- Methodology: {s.get('methodology')}\n"
            f"- Findings: {s.get('findings')}\n"
            f"- Limitations: {s.get('limitations')}\n"
        )
    summaries_data = "\n\n".join(serialized_summaries)
    
    prompt = CRITIC_PROMPT.format(
        topic=topic,
        summaries_data=summaries_data
    )
    
    try:
        criticism_report = call_gemini(prompt=prompt)
    except Exception as e:
        print(f"Critic synthesis failed: {e}")
        criticism_report = f"# Critical Synthesis: {topic}\nCritical synthesis failed to compile due to model limitations."
        
    print("Completed critical synthesis report.")
    return {
        "criticism": criticism_report,
        "status": "gaps"
    }
