import os
import tempfile
import shutil
import pytest

from backend.services.report_service import ReportService

def test_report_compilation():
    """
    Test that ReportService parses Markdown syntax and successfully compiles a valid, non-empty PDF.
    """
    temp_dir = tempfile.mkdtemp()
    
    try:
        report_service = ReportService(output_dir=temp_dir)
        
        mock_markdown = """# ResearchPilot Literature Survey Report: Test Topic

This is a comprehensive literature survey report created during automated pytest testing.

## Executive Summary
This report analyzes core preprints in the target field, showing a high level of synthetic alignment.

## Literature Survey & Paper Summaries
Here is a comparison matrix of the key papers:

| Paper Title | Authors | Methodology | Core Findings |
|---|---|---|---|
| Attention is All You Need | Vaswani et al. | Transformer Architecture | Achieved SOTA in machine translation |
| Adam Optimization | Kingma et al. | Stochastic Gradient Descent | Premium convergence speeds |

## Critical Analysis
Most evaluated preprints rely heavily on empirical hyperparameter grids rather than rigorous proof-theoretic structures.

- **Limitation 1**: High resource training envelopes.
- **Limitation 2**: Lack of interpretability layers.

## Tiered Learning Roadmap
Here is the recommended study path:

### Beginner Level
- **Concepts**: Linear algebra, vector spaces, gradient descent.
- **Reading**: Intro to Stochastic Processes.
- **Projects**: Write a single neuron perceptron from scratch in python.
"""
        pdf_filename = "test_survey_report.pdf"
        pdf_path = report_service.generate_pdf(mock_markdown, pdf_filename)
        
        # Verify file is compiled
        assert pdf_path != ""
        assert os.path.exists(pdf_path)
        # Verify file is not empty
        assert os.path.getsize(pdf_path) > 0
        
    finally:
        # Clean up temp folder
        shutil.rmtree(temp_dir)
