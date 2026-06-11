from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

# Define the State shared across all nodes in the Graph
class ResearchState(TypedDict):
    topic: str
    papers: List[Dict[str, Any]]
    summaries: List[Dict[str, Any]]
    criticism: str
    gaps: Dict[str, Any]
    roadmap: Dict[str, Any]
    report_markdown: str
    report_path: str
    job_id: str
    status: str

# Import Agent Nodes
from backend.agents.search_agent import search_node
from backend.agents.retrieval_agent import retrieval_node
from backend.agents.summarize_agent import summarize_node
from backend.agents.critic_agent import critic_node
from backend.agents.gap_agent import gap_node
from backend.agents.roadmap_agent import roadmap_node
from backend.agents.report_agent import report_node

# Construct the StateGraph
workflow = StateGraph(ResearchState)

# Register Node Functions
workflow.add_node("search", search_node)
workflow.add_node("retrieve", retrieval_node)
workflow.add_node("summarize", summarize_node)
workflow.add_node("critic", critic_node)
workflow.add_node("gap", gap_node)
workflow.add_node("build_roadmap", roadmap_node)
workflow.add_node("report", report_node)

# Set Entry Point
workflow.set_entry_point("search")

# Establish Linear Research Pipeline Edges
workflow.add_edge("search", "retrieve")
workflow.add_edge("retrieve", "summarize")
workflow.add_edge("summarize", "critic")
workflow.add_edge("critic", "gap")
workflow.add_edge("gap", "build_roadmap")
workflow.add_edge("build_roadmap", "report")
workflow.add_edge("report", END)


# Compile Graph
research_graph = workflow.compile()
print("LangGraph Multi-Agent Workflow compiled successfully.")
