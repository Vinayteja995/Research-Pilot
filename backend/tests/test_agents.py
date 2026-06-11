import os
import unittest.mock as mock
import pytest

from backend.agents.search_agent import search_node
from backend.agents.summarize_agent import summarize_node
from backend.agents.critic_agent import critic_node
from backend.agents.gap_agent import gap_node
from backend.agents.roadmap_agent import roadmap_node
from backend.agents.report_agent import report_node

@mock.patch("backend.agents.search_agent.call_gemini")
@mock.patch("backend.agents.search_agent.ArxivService")
def test_search_node(MockArxivService, mock_call_gemini):
    """
    Test that the Search Agent Node generates queries, queries arXiv, and populates the papers state.
    """
    # Setup mock query data
    mock_call_gemini.return_value = '{"queries": ["quantum computing NLP", "LLM quantum logic"]}'
    
    # Setup mock arXiv service
    arxiv_instance = MockArxivService.return_value
    arxiv_instance.search_papers.return_value = [
        {
            "id": "123.456",
            "title": "Quantum Attention Mechanisms",
            "authors": "Alice Smith",
            "abstract": "Quantum computing applied to natural language transformers.",
            "url": "arxiv.org/123.456",
            "pdf_url": "arxiv.org/pdf/123.456.pdf",
            "published": "2024-01-01"
        }
    ]
    
    state = {"topic": "Quantum Natural Language Processing", "papers": []}
    output = search_node(state)
    
    assert "papers" in output
    assert len(output["papers"]) == 1
    assert output["papers"][0]["title"] == "Quantum Attention Mechanisms"
    assert output["status"] == "retrieving"

@mock.patch("backend.agents.summarize_agent.call_gemini")
def test_summarize_node(mock_call_gemini):
    """
    Test that Summarize Node calls Gemini to yield structured objective-limitation summaries.
    """
    mock_call_gemini.return_value = """{
        "paper_id": "123.456",
        "title": "Quantum Attention Mechanisms",
        "objective": "Build a quantum-mechanical transformer.",
        "methodology": "Simulated quantum gates.",
        "findings": "Improved convergence over classical models.",
        "limitations": "No hardware deployment yet."
    }"""
    
    state = {
        "papers": [
            {
                "id": "123.456",
                "title": "Quantum Attention Mechanisms",
                "authors": "Alice Smith",
                "abstract": "Quantum computing applied to transformers."
            }
        ]
    }
    
    output = summarize_node(state)
    
    assert "summaries" in output
    assert len(output["summaries"]) == 1
    assert output["summaries"][0]["paper_id"] == "123.456"
    assert output["summaries"][0]["objective"] == "Build a quantum-mechanical transformer."
    assert output["status"] == "criticizing"

@mock.patch("backend.agents.critic_agent.call_gemini")
def test_critic_node(mock_call_gemini):
    """
    Test that Critic Node produces a synthesized review.
    """
    mock_call_gemini.return_value = "### Critique Analysis\nDisagreements in simulation metrics are present."
    
    state = {
        "topic": "Quantum NLP",
        "summaries": [
            {
                "paper_id": "123.456",
                "title": "Quantum Attention Mechanisms",
                "objective": "Test",
                "methodology": "Test",
                "findings": "Test",
                "limitations": "Test"
            }
        ]
    }
    
    output = critic_node(state)
    
    assert "criticism" in output
    assert "Critique Analysis" in output["criticism"]
    assert output["status"] == "gaps"

@mock.patch("backend.agents.gap_agent.call_gemini")
def test_gap_node(mock_call_gemini):
    """
    Test that Gap Node successfully extracts open problems.
    """
    mock_call_gemini.return_value = """{
        "gaps": [
            {
                "title": "Hardware Saturation Limitations",
                "description": "Lack of real-world hardware tests.",
                "implications": "Prevents industrial uptake.",
                "proposed_approach": "Develop cross-platform hardware adapters."
            }
        ]
    }"""
    
    state = {"topic": "Quantum NLP", "summaries": [], "criticism": "Mock Criticism"}
    output = gap_node(state)
    
    assert "gaps" in output
    assert len(output["gaps"]["gaps"]) == 1
    assert output["gaps"]["gaps"][0]["title"] == "Hardware Saturation Limitations"
    assert output["status"] == "roadmap"
