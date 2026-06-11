# Prompt templates for the 7 research agents.

SEARCH_QUERY_PROMPT = """You are an expert academic research director.
The user wants to research the following topic: "{topic}"

Generate 3 to 4 distinct, highly effective search queries for the arXiv API. 
These queries should cover different aspects of the topic (e.g., core methodologies, applications, comparative analyses, theory).
Make sure the queries are search engine-friendly, using standard keyword terms.

Your response must be in JSON format:
{{
  "queries": [
    "query 1",
    "query 2",
    "query 3"
  ]
}}
"""

SUMMARIZATION_PROMPT = """You are an elite academic peer-reviewer and researcher.
You are given the following paper:
Title: {title}
Authors: {authors}
Abstract: {abstract}

Analyze the paper and produce a high-quality structured summary.
Your summary must contain the following fields:
1. **Objective**: What is the primary problem this paper solves and what is its goal?
2. **Methodology**: What approaches, architectures, datasets, or theoretical frameworks did they use?
3. **Findings**: What are the key results, metrics, or insights discovered?
4. **Limitations**: What are the weak points, assumptions, or constraints of the paper as acknowledged by the authors or visible to you?

Output MUST be a JSON object with this exact structure:
{{
  "paper_id": "{paper_id}",
  "title": "{title}",
  "objective": "Detailed objective of the paper...",
  "methodology": "Step-by-step methodology...",
  "findings": "Key findings and metrics...",
  "limitations": "Acknowledged or observed limitations..."
}}
"""

CRITIC_PROMPT = """You are an extremely analytical and rigorous academic critic.
You have been given a set of structured summaries of papers related to the topic: "{topic}"

Summaries:
{summaries_data}

Analyze this body of work comprehensively. Identify:
1. **Contradictions & Disagreements**: Where do these papers disagree in terms of findings, assumptions, or optimal solutions?
2. **Methodological Weaknesses**: What are common flaws, small sample sizes, simplistic assumptions, or oversimplified evaluations across these papers?
3. **Missing Perspectives**: What critical aspects, real-world constraints, or alternative approaches are ignored by this group of papers?
4. **Level of Evidence**: Evaluate if the claims made in these papers are backed by strong empirical evidence or if they are largely theoretical.

Produce a detailed, professional critical analysis report in Markdown. Be academic, precise, and objective.
"""

GAP_PROMPT = """You are an innovative academic visionary who specializes in finding research opportunities.
You are given a collection of paper summaries and a critical analysis of them:

Topic: "{topic}"

Paper Summaries:
{summaries_data}

Critical Analysis:
{criticism_data}

Your task is to identify 3 to 5 significant **Research Gaps** and **Open Problems** in this field that represent excellent opportunities for future research.
For each gap/problem, provide:
1. **Title**: A clear name for the research gap.
2. **Description**: What is the gap and why has it not been solved yet?
3. **Implications**: Why is solving this gap important for the industry or academia?
4. **Proposed Approach**: A suggested, high-level technical path, methodology, or experiment that a future researcher could pursue to solve this gap.

Your response must be in JSON format:
{{
  "gaps": [
    {{
      "title": "Research Gap Title",
      "description": "Why it's a gap...",
      "implications": "What happens if we solve it...",
      "proposed_approach": "Suggested path to solve..."
    }}
  ]
}}
"""

ROADMAP_PROMPT = """You are an inspiring educator and technical mentor.
Based on the papers, research summaries, and identified research gaps in "{topic}", compile a comprehensive, highly-structured learning path for a student or engineer wanting to become a world-class researcher or practitioner in this domain.

Provide a syllabus categorized into three levels:
1. **Beginner**: Foundational concepts, prerequisites, key papers to read first, and basic coding/modeling tasks.
2. **Intermediate**: Core advanced techniques, mathematical formulations, reproduction projects, and standard tooling.
3. **Advanced**: Cutting-edge topics, state-of-the-art open questions, novel research ideas, and complex system implementations.

For each level, list:
- Core concepts to master
- Key reading or papers
- Practical project or exercises

Your response must be in JSON format:
{{
  "beginner": {{
    "concepts": ["Concept 1", "Concept 2"],
    "reading": ["Paper/Resource 1", "Paper/Resource 2"],
    "projects": ["Project 1"]
  }},
  "intermediate": {{
    "concepts": ["Concept 1", "Concept 2"],
    "reading": ["Paper/Resource 1", "Paper/Resource 2"],
    "projects": ["Project 1"]
  }},
  "advanced": {{
    "concepts": ["Concept 1", "Concept 2"],
    "reading": ["Paper/Resource 1", "Paper/Resource 2"],
    "projects": ["Project 1"]
  }}
}}
"""

REPORT_PROMPT = """You are a senior research scientist drafting a state-of-the-art literature survey report.
Compile all the research findings gathered for the topic: "{topic}"

Here are the collected materials:
- Paper Summaries: {summaries_data}
- Critical Analysis: {criticism_data}
- Research Gaps: {gaps_data}
- Learning Roadmap: {roadmap_data}

Assemble these elements into a comprehensive, professionally formatted Literature Survey Report.
The report must include the following sections, formatted in structured Markdown:

1. **Title**: A professional academic survey title
2. **Executive Summary**: A concise, high-impact summary of the domain and findings.
3. **Introduction & Context**: Background on '{topic}', why it's important, and the current landscape.
4. **Literature Survey & Paper Summaries**: Detailed, formatted reviews of the key papers, outlining objectives, methodologies, findings, and limitations. Include a comparison table showing Paper Title, Authors, Methodology, and Core Findings.
5. **Critical Analysis**: The critical synthesis of the current body of work.
6. **Identified Research Gaps**: A clear list of open problems and future opportunities.
7. **Future Directions & Learning Roadmap**: Integrating the tiered roadmap.
8. **Conclusion**: Final synthesis and outlook.
9. **References**: A formal bibliography listing the researched papers (Title, Authors, URL).

Use academic tone, structured bullet points, clear headings, and table formatting where appropriate.
"""
