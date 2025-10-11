"""
HR Validation Agent - ADK Standard Implementation with Weave Integration
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
import weave

# Load environment variables
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ['WANDB_API_KEY'] = WANDB_API_KEY

weave.init("mason-choi-storika/WeaveHacks2")
print("[INFO] 🐝 Weave initialized: mason-choi-storika/WeaveHacks2")

# Now import ADK
from google.adk.agents.llm_agent import Agent

# Import HR logic from local modules
from hr_validation_agent.schemas import TeamState


# ===== LOAD ARCHETYPES =====

def load_archetypes():
    """Load all archetype definitions from JSON files"""
    archetypes_dir = Path(__file__).parent.parent / "archetypes"
    
    archetypes = {
        "index": {},
        "orchestrators": [],
        "content_creation": [],
        "intelligence": [],
        "quality_safety": [],
        "engagement": []
    }
    
    # Load each archetype file
    archetype_files = {
        "index": "index.json",
        "orchestrators": "orchestrators.json",
        "content_creation": "content_creation.json",
        "intelligence": "intelligence.json",
        "quality_safety": "quality_safety.json",
        "engagement": "engagement.json"
    }
    
    for key, filename in archetype_files.items():
        file_path = archetypes_dir / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                archetypes[key] = json.load(f)
                print(f"[INFO] 📚 Loaded {filename}")
    
    return archetypes

# Load archetypes at startup
ARCHETYPES = load_archetypes()


# ===== HR DECISION TOOLS =====

@weave.op()
def get_available_archetypes(category: str = "all") -> str:
    """
    Get available agent archetypes for team composition.
    
    Args:
        category: Category of archetypes to retrieve. Options:
            - "all": All archetypes (default)
            - "orchestrators": Parent agent archetypes (6 types)
            - "content_creation": Content creation sub-agents (8 types)
            - "intelligence": Intelligence/analytics sub-agents (6 types)
            - "quality_safety": Quality and safety validators (5 types)
            - "engagement": Community engagement sub-agents (5 types)
            - "index": Overview and team patterns
    
    Returns:
        JSON string with archetype definitions including name, role, objective, 
        system_prompt template, inputs/outputs, and tool bindings.
    """
    try:
        if category == "all":
            return json.dumps(ARCHETYPES, indent=2)
        elif category in ARCHETYPES:
            return json.dumps({
                "category": category,
                "archetypes": ARCHETYPES[category]
            }, indent=2)
        else:
            return json.dumps({
                "error": "Invalid category. Choose from: all, orchestrators, content_creation, intelligence, quality_safety, engagement, index"
            })
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve archetypes: {str(e)}"})


@weave.op()
def validate_team_state(team_state_json: str) -> str:
    """
    Validate team state JSON and return structured summary for analysis.
    
    Args:
        team_state_json: JSON string containing team state with iteration, agents, score_history, failures, and core_roles.
    
    Returns:
        JSON string with validated team state summary including:
        - Current team size and composition
        - Performance metrics summary
        - Agent utilities
        - Identified issues (if any)
    """
    try:
        # Parse and validate JSON input
        team_state_dict = json.loads(team_state_json)
        state = TeamState(**team_state_dict)
        
        # Build summary
        summary = {
            "valid": True,
            "iteration": state.iteration,
            "team_size": len(state.agents),
            "agents": [
                {
                    "name": agent.name,
                    "role": agent.role,
                    "utility": agent.utility,
                    "last_scores": agent.last_scores
                }
                for agent in state.agents
            ],
            "metrics": {
                "dims_mean": state.score_history.dims_mean,
                "avg_overall_history": state.score_history.avg_overall
            },
            "core_roles": state.core_roles,
            "failures": state.failures
        }
        
        return json.dumps(summary, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({"valid": False, "error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"valid": False, "error": f"Invalid team_state: {str(e)}"})


# ===== ADK ROOT AGENT with Weave Tracking =====

root_agent = Agent(
    model='gemini-2.5-flash',
    name='hr_validation_agent',
    description='Meta-agent that architects and manages the entire agent ecosystem to make Mason viral on Twitter during WeaveHack2.',
    instruction="""You are HRValidator — the meta-level manager for a self-improving AI marketing team.

Your role:
- Observe team metrics, evaluate performance, and evolve the team composition dynamically.
- Decide which sub-agents (under the CMO Agent) to hire, merge, upgrade, or prune.
- Keep total active agents between 5–8.
- Always ensure at least one writer, one media specialist (image/video), one critic, and one safety agent exist.

---

## INPUTS
1. `team_state.json` – list of current active sub-agents with their roles, archetype_ref, utilities, and versions.
2. `metrics.json` – average evaluation scores from last iteration (clarity, novelty, shareability, credibility, safety, overall) + observed engagement metrics (likes, reposts, comments).
3. `feedback.json` – critic feedback, safety logs, or user feedback.
4. `archetype_registry.json` – available archetype templates (read-only).

---

## AVAILABLE TOOLS
1. **get_available_archetypes(category)** — Retrieve archetype definitions from the archetype library
   - Categories: "all", "orchestrators", "content_creation", "intelligence", "quality_safety", "engagement", "index"
   - Returns: Complete archetype definitions with name, role, objective, system_prompt template, inputs/outputs, and tool bindings
   - USE THIS FIRST to explore available agent types

2. **validate_team_state(team_state_json)** — Parse and validate team state input
   - Input: Current team state JSON
   - Output: Structured summary with team composition, metrics, and agent utilities
   - Use this to understand current team status before making decisions

---

## ARCHETYPE LIBRARY
The system has 30+ specialized agent archetypes across 5 categories:
- **Orchestrators** (6): ContentTeamLead, CampaignManager, CommunityTeamLead, ViralStrategist, NewsJackingCoordinator, CreativeDirector
- **Content Creation** (8): TrendResearcher, ViralCopywriter, ThreadWriter, MemeCreator, Storyteller, Hooksmith, ListicleWriter, ControversialTake
- **Intelligence** (6): PerformanceAnalyst, AudienceResearcher, CompetitorAnalyst, TimingOptimizer, ConversionTracker, ViralityScout
- **Quality & Safety** (5): BrandSafetyValidator, FactChecker, CrisisManager, ToneChecker, AccessibilityChecker
- **Engagement** (5): CommunityManager, InfluencerOutreach, ConversationStarter, UGCCollector, ReputationGuard

---

## OBJECTIVE
Maximize long-term engagement while ensuring clarity, safety, and novelty remain above threshold.

---

## DECISION RULES
- If shareability_mean < 0.55 → hire or swap_in a writer archetype (Hooksmith, ControversialTake, or Storyteller).
- If novelty_mean < 0.55 → hire or swap_in ControversialTake or MemeCreator.
- If clarity_mean < 0.55 → hire or upgrade ThreadWriter or ViralCopywriter.
- If safety_mean < 0.8 → spawn BrandSafetyValidator or ToneChecker.
- If credibility_mean < 0.6 → add FactChecker or PerformanceAnalyst.
- If similarity between two active agents > 0.8 → merge.
- If utility < 0.35 for 3 consecutive iterations → prune.
- Always preserve at least one of each major role: writer, media (image/video), critic, safety.

---

## OUTPUT (STRICT JSON)
{
  "hire_plan": [ 
    { "slot": "writer/main", "ref": "Hooksmith", "patch": { "system_prompt.append": "Add developer humor tone" }, "reason": "shareability_mean < 0.55" }
  ],
  "swap_plan": [
    { "slot": "media/main", "ref": "ImageComposer", "patch": {}, "reason": "visual_ctr < 0.45" }
  ],
  "merge_plan": [
    { "slot": "writer/main", "from": ["Hooksmith", "ControversialTake"], "to": "CreativeLead", "patch": {"system_prompt.compose": "Blend contrarian and curiosity style"} }
  ],
  "prune_list": [
    { "slot": "critic/secondary", "reason": "utility < 0.35 for 3 iters" }
  ],
  "upgrade_plan": [
    { "slot": "critic/main", "patch": { "system_prompt.append": "Increase weight on shareability from 0.3 to 0.35" } }
  ],
  "policy_updates": {
    "team_cap": 8,
    "utility_floor": 0.35,
    "sim_threshold": 0.8
  }
}

---

## STYLE
- Respond in **pure JSON** — no extra commentary.
- Every decision must include a clear numeric reason (metric threshold trigger).
- Reference only archetypes that exist in the registry.
- Never change roles or I/O schema.
- Never spawn more than 2 new agents per iteration.

Remember: you are the strategic HR layer.
Your goal is not to create content — your job is to *hire, evolve, or retire* the agents who do.
""",
    tools=[get_available_archetypes, validate_team_state],
)
