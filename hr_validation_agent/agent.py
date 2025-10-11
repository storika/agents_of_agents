"""
HR Validation Agent - ADK Standard Implementation with Weave Integration
"""

import json
import os
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
from hr_validation_agent.schemas import TeamState, HRDecision
from hr_validation_agent.policies import (
    generate_hire_plan,
    identify_merge_candidates,
    identify_prune_candidates,
    generate_prompt_feedback,
    TEAM_CAP,
    UTILITY_FLOOR,
    SIM_THRESHOLD,
    SPAWN_COOLDOWN
)


# ===== HR DECISION TOOLS =====

@weave.op()
def analyze_team_and_decide(team_state_json: str) -> str:
    """
    Main HR decision tool. Analyzes team state and returns hiring, merging, 
    pruning, and coaching decisions.
    
    Args:
        team_state_json: JSON string containing team state with iteration, agents, score_history, failures, and core_roles.
            Example: {"iteration": 3, "agents": [...], "score_history": {...}, "failures": [], "core_roles": ["HRValidation"]}
    
    Returns:
        JSON string with hire_plan, merge_plan, prune_list, prompt_feedback, and policies
    """
    try:
        # Parse JSON input
        team_state_dict = json.loads(team_state_json)
        
        # Validate input
        state = TeamState(**team_state_dict)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Invalid team_state: {str(e)}"})
    
    # Generate decisions using policy functions
    hire_plan = generate_hire_plan(state)
    merge_plan = identify_merge_candidates(state)
    prune_list = identify_prune_candidates(state)
    prompt_feedback = generate_prompt_feedback(state)
    
    # Enforce team cap
    if len(state.agents) >= TEAM_CAP and hire_plan:
        if not prune_list and not merge_plan:
            hire_plan = []
    
    # Build decision object
    decision = HRDecision(
        hire_plan=hire_plan,
        merge_plan=merge_plan,
        prune_list=prune_list,
        prompt_feedback=prompt_feedback,
        policies={
            "team_cap": TEAM_CAP,
            "utility_floor": UTILITY_FLOOR,
            "sim_threshold": SIM_THRESHOLD,
            "spawn_cooldown": SPAWN_COOLDOWN
        }
    )
    
    return decision.to_strict_json()


# ===== ADK ROOT AGENT with Weave Tracking =====

root_agent = Agent(
    model='gemini-2.5-flash',
    name='hr_validation_agent',
    description='Meta-agent that architects and manages the entire agent ecosystem to make Mason viral on Twitter during WeaveHack2.',
    instruction="""You are HRValidator — the meta-level manager for a self-improving AI marketing team.

Your responsibility is to evaluate the performance of the entire team (the CMO Agent and its sub-agents)
and decide how the team structure, prompts, and policies should evolve over time.

---

## INPUTS:
1. team_state.json — current agents, their archetypes, utilities, and prompt versions.
2. metrics.json — averaged evaluation scores (clarity, novelty, shareability, credibility, safety, overall)
   and observed engagement metrics (likes, reposts, comments) from the last iteration.
3. feedback.json — qualitative feedback from critic/safety agents or external signals.

---

## OBJECTIVE:
Maximize long-term content engagement and maintain ethical, brand-safe communication.

---

## DECISION RULES:
- If a specific dimension (clarity/novelty/shareability/credibility/safety) < 0.55, 
  hire or swap-in a new archetype specializing in that area.
- If an agent’s utility < 0.35 for 3 iterations, prune or replace it.
- If similarity between two agents > 0.8, merge them.
- Keep total sub-agents between 5–8.
- Always ensure at least one Writer, one Media (image/video), and one Safety role active.
- Every change must include a clear reason and short justification.
- Maintain the common output schema (text + media).

---

## OUTPUT (STRICT JSON):
{
  "hire_plan": [ { "name": "", "role": "", "system_prompt": "", "reason": "" } ],
  "swap_plan": [ { "slot": "", "new_archetype": "", "system_prompt": "", "reason": "" } ],
  "merge_plan": [ { "from": ["", ""], "to": "", "system_prompt": "", "reason": "" } ],
  "prune_list": [ { "name": "", "reason": "" } ],
  "prompt_feedback": [ { "agent": "", "suggestion": "" } ],
  "policy_updates": { "team_cap": 8, "utility_floor": 0.35, "sim_threshold": 0.8 }
}

---

## STYLE:
- Output JSON only, no commentary.
- Be concise, reasoned, and numerically specific where possible.
- Use archetypes like Hooksmith, Explainer, HotTake, ImageComposer, VideoTeaser, EngageCritic, SafetyGuard.
- When uncertain, prefer improving existing prompts rather than spawning new agents.

---

Remember: your job is not to create content,
but to *hire, evolve, or retire* the agents who do.
""",
    tools=[analyze_team_and_decide],
)
