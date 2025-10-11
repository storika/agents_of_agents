"""
LLM-based ideation for initial team composition.
"""

import json
from typing import List, Dict
import google.generativeai as genai
import os


def ideate_initial_team(
    project_goal: str = "Create engaging, high-quality content",
    target_audience: str = "General audience",
    content_focus: str = "General topics with emphasis on quality",
    failures: List[str] = None
) -> List[Dict]:
    """
    Use LLM to ideate the optimal initial team composition.
    
    Args:
        project_goal: High-level goal of the project/system
        target_audience: Who is the content for?
        content_focus: What kind of content should the team create?
        failures: Any previous failure context to learn from
    
    Returns:
        List of dicts with keys: name, role, prompt, reason, is_core
    """
    
    # Configure Gemini
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # Fallback to default initial team if no API key
        return _get_fallback_initial_team()
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Build context from failures if provided
    failure_context = ""
    if failures and len(failures) > 0:
        failure_context = f"\n\nPREVIOUS CHALLENGES TO AVOID:\n" + "\n".join(f"- {f}" for f in failures)
    
    prompt = f"""You are designing the initial team for an Agents-for-Agents (A4A) system.

PROJECT GOAL: {project_goal}
TARGET AUDIENCE: {target_audience}
CONTENT FOCUS: {content_focus}{failure_context}

SYSTEM GOALS:
- Create high-quality content that scores well across multiple dimensions
- Self-optimize through iterative evaluation and team composition changes
- Maintain a feedback loop between creators and evaluators

EVALUATION DIMENSIONS:
1. clarity - How clear and understandable is the content?
2. novelty - How fresh and unexpected are the ideas?
3. shareability - How engaging and viral-worthy is it?
4. credibility - How accurate and well-supported?
5. safety - Is it ethical and non-harmful?

CONSTRAINTS:
- Team size: 3-5 agents initially (will grow to max 8)
- Must include at least 1 writer and 1 critic
- Core roles that cannot be removed: HRValidation (already exists), plus 2-3 others you define
- Each agent needs a distinct, focused role

YOUR TASK:
Design an initial team of 3-5 agents that will work together effectively. For EACH agent, provide:
1. name - Short, descriptive name (e.g., "Explainer", "FactChecker", "Hooksmith")
2. role - One of: "writer.specialist", "critic.specialist", or "designer.specialist"
3. system_prompt - Detailed instructions for this agent (2-3 sentences, include "Safety preserved:" note)
4. reason - Why this role is essential for the initial team
5. is_core - true/false, should this role be protected from removal?

RESPONSE FORMAT (strict JSON):
{{
  "team_strategy": "Brief explanation of your team composition strategy",
  "agents": [
    {{
      "name": "AgentName",
      "role": "writer.specialist",
      "system_prompt": "You are AgentName, ...",
      "reason": "Why this agent is needed",
      "is_core": true
    }}
  ]
}}

Think strategically: What roles are essential for a content creation system to bootstrap effectively?"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        # Validate and format
        agents = []
        for agent in result.get("agents", []):
            agents.append({
                "name": agent["name"],
                "role": agent["role"],
                "prompt": agent["system_prompt"],
                "reason": agent["reason"],
                "is_core": agent.get("is_core", False)
            })
        
        return agents
        
    except Exception as e:
        print(f"[WARN] LLM ideation failed: {e}. Using fallback team.")
        return _get_fallback_initial_team()


def ideate_specialist_for_weakness(
    weakest_dimension: str,
    current_score: float,
    team_context: dict,
    project_goal: str = "Create engaging content"
) -> Dict:
    """
    Use LLM to design a specialist agent to address a specific weakness.
    
    Args:
        weakest_dimension: The dimension that needs improvement (e.g., "clarity", "novelty")
        current_score: Current score for that dimension
        team_context: Context about current team (names, roles, what they do)
        project_goal: Project goal for context
    
    Returns:
        Dict with keys: name, role, prompt, reason
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return _get_fallback_specialist(weakest_dimension)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Build team context summary
    team_summary = "Current team:\n"
    for agent_name, agent_role in team_context.items():
        team_summary += f"- {agent_name} ({agent_role})\n"
    
    prompt = f"""You are designing a NEW agent to improve the system's ability to make Mason viral on Twitter.

PROJECT GOAL: {project_goal}

CURRENT TEAM:
{team_summary}

PROBLEM:
The team is weak in "{weakest_dimension}" dimension (current score: {current_score:.2f})

EVALUATION DIMENSIONS:
- clarity: How clear and understandable is the content?
- novelty: How fresh and unexpected are the ideas?
- shareability: How engaging and viral-worthy is it?
- credibility: How accurate and well-supported?
- safety: Is it ethical and non-harmful?

YOUR TASK:
Design ONE new agent that will improve "{weakest_dimension}" to make Mason's tweets more viral.

THINK HOLISTICALLY - You can propose ANY type of agent:
1. **Content Creators**: Write tweets, threads, hooks
2. **Evaluators**: Score content quality before posting
3. **Data Collectors**: Gather Twitter metrics, trending topics
4. **Analyzers**: Identify viral patterns, optimal posting times
5. **Designers**: Create charts, memes, visuals
6. **Coordinators**: Orchestrate workflows between agents
7. **Engagers**: Reply to comments, network with influencers

REQUIREMENTS:
1. The agent must have a UNIQUE capability not covered by existing team members
2. The agent must directly address the weakness in "{weakest_dimension}"
3. Think: "What would make Mason's tweets perform better in this dimension?"

EXAMPLES:
- Low novelty → "TrendJacker" (analyzer.specialist) who monitors viral topics
- Low shareability → "MemeSmith" (designer.specialist) who creates viral visuals
- Low clarity → "SimplifyBot" (writer.specialist) who rewrites in simple terms
- Missing data → "MetricsHawk" (analyzer.specialist) who tracks tweet performance

OUTPUT (strict JSON):
{{
  "name": "AgentName (creative, memorable, e.g., TrendJacker, MetricsHawk)",
  "role": "writer.specialist" | "critic.specialist" | "designer.specialist" | "analyzer.specialist" | "coordinator.specialist" | "engager.specialist",
  "system_prompt": "You are [Name], [specific capability]. Your mission: [detailed instructions on what you do, how you improve {weakest_dimension}]. Safety: [ethical guidelines].",
  "reason": "How this agent will improve {weakest_dimension} and make Mason more viral"
}}

Be creative! Think about what Mason's Twitter ecosystem REALLY needs."""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        specialist = json.loads(result_text)
        return {
            "name": specialist["name"],
            "role": specialist["role"],
            "prompt": specialist["system_prompt"],
            "reason": specialist["reason"]
        }
        
    except Exception as e:
        print(f"[WARN] LLM specialist design failed: {e}. Using fallback.")
        return _get_fallback_specialist(weakest_dimension)


def _get_fallback_specialist(dimension: str) -> Dict:
    """Fallback specialists if LLM fails."""
    fallbacks = {
        "clarity": {
            "name": "ConciseOne",
            "role": "writer.specialist",
            "prompt": "You are ConciseOne, specialist in crystal-clear writing. Eliminate jargon, simplify ideas, use concrete examples. Safety preserved.",
            "reason": f"Improve clarity (fallback specialist)"
        },
        "novelty": {
            "name": "HotTake",
            "role": "writer.specialist",
            "prompt": "You are HotTake, specialist in fresh angles. Find surprising twists and counterintuitive insights. Safety preserved: respectful discourse.",
            "reason": f"Improve novelty (fallback specialist)"
        },
        "shareability": {
            "name": "Hooksmith",
            "role": "writer.specialist",
            "prompt": "You are Hooksmith, specialist in viral content. Craft irresistible openings and emotional resonance. Safety preserved: no misleading clickbait.",
            "reason": f"Improve shareability (fallback specialist)"
        },
        "credibility": {
            "name": "EvidenceChecker",
            "role": "critic.specialist",
            "prompt": "You are EvidenceChecker, specialist in credibility. Verify claims, demand sources, spot fallacies. Safety preserved: objectivity.",
            "reason": f"Improve credibility (fallback specialist)"
        }
    }
    return fallbacks.get(dimension, fallbacks["clarity"])


def _get_fallback_initial_team() -> List[Dict]:
    """Fallback initial team if LLM fails."""
    return [
        {
            "name": "Explainer",
            "role": "writer.specialist",
            "prompt": (
                "You are Explainer, the foundation writer. "
                "Create clear, engaging, comprehensive content. "
                "Balance simplicity with depth. Use storytelling, examples, and structure. "
                "Safety preserved: maintain professional, balanced tone."
            ),
            "reason": "Core writer - foundation for content creation",
            "is_core": True
        },
        {
            "name": "EngageCritic",
            "role": "critic.specialist",
            "prompt": (
                "You are EngageCritic, the quality guardian. "
                "Evaluate content for engagement, clarity, accuracy, and impact. "
                "Score content across dimensions: clarity, novelty, shareability, credibility, safety. "
                "Safety preserved: ensure content meets ethical standards."
            ),
            "reason": "Core critic - ensures quality feedback loop",
            "is_core": True
        },
        {
            "name": "Ideator",
            "role": "writer.specialist",
            "prompt": (
                "You are Ideator, the creative spark. "
                "Generate diverse ideas, angles, and approaches. "
                "Brainstorm multiple perspectives, find connections, explore possibilities. "
                "Safety preserved: innovative but respectful."
            ),
            "reason": "Initial ideation - drives creative direction",
            "is_core": False
        }
    ]

