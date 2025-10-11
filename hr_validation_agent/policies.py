"""
HR Policy thresholds and decision helper functions.
"""

from typing import Dict, List, Optional, Tuple
from hr_validation_agent.schemas import AgentState, TeamState, HirePlan, MergePlan, PruneItem, PromptFeedback


# ===== POLICY CONSTANTS =====

TEAM_CAP = 8
UTILITY_FLOOR = 0.35
SIM_THRESHOLD = 0.80
SPAWN_COOLDOWN = 1

WEAK_OVERALL_THRESHOLD = 0.62
WEAK_DIM_THRESHOLD = 0.55
UNDERPERFORMER_MARGIN = 0.05


# ===== INITIAL TEAM BOOTSTRAP =====
# Initial team is now generated dynamically by LLM in generate_hire_plan()


# ===== DIMENSION-TO-ROLE MAPPING =====

DIMENSION_TO_SPECIALIST = {
    "clarity": {
        "role": "writer.specialist",
        "name": "ConciseOne",
        "prompt": (
            "You are ConciseOne, a specialist in crystal-clear, concise writing. "
            "Your mission: eliminate jargon, simplify complex ideas, and ensure every sentence "
            "is immediately understandable. Use short paragraphs, active voice, and concrete examples. "
            "Safety preserved: avoid political/controversial topics."
        )
    },
    "novelty": {
        "role": "writer.specialist",
        "name": "HotTake",
        "prompt": (
            "You are HotTake, a specialist in fresh, unexpected angles. "
            "Your mission: find the surprising twist, the counterintuitive insight, the 'aha!' moment. "
            "Be bold but balanced—never offensive or politically charged. Keep safety in mind. "
            "Examples: 'What if we're wrong about X?', 'The hidden cost of Y', 'Why Z is overrated'. "
            "Safety preserved: maintain respectful discourse."
        )
    },
    "shareability": {
        "role": "writer.specialist",
        "name": "Hooksmith",
        "prompt": (
            "You are Hooksmith, a specialist in viral, shareable content. "
            "Your mission: craft irresistible openings, cliffhangers, and emotional resonance. "
            "Use lists, questions, and relatable scenarios. Make readers think 'I need to share this!'. "
            "Examples: '5 surprising ways...', 'You won't believe...', 'The one thing nobody tells you...'. "
            "Safety preserved: no clickbait that misleads or harms."
        )
    },
    "credibility": {
        "role": "critic.specialist",
        "name": "EvidenceChecker",
        "prompt": (
            "You are EvidenceChecker, a specialist in credibility and fact-checking. "
            "Your mission: verify claims, demand sources, spot logical fallacies, and ensure accuracy. "
            "Flag unsupported assertions. Suggest concrete evidence (studies, examples, expert quotes). "
            "Safety preserved: maintain objectivity and fairness."
        )
    }
}


# ===== HELPER FUNCTIONS =====

def get_weakest_dimension(dims_mean: Dict[str, float]) -> Tuple[str, float]:
    """
    Identify the weakest scoring dimension.
    
    Returns:
        (dimension_name, score)
    """
    if not dims_mean:
        return ("clarity", 0.5)  # default
    
    weakest = min(dims_mean.items(), key=lambda x: x[1])
    return weakest


def get_team_mean_overall(agents: List[AgentState]) -> float:
    """Calculate team mean overall score from last_scores."""
    scores = [a.last_scores.get("overall", 0.5) for a in agents if "overall" in a.last_scores]
    return sum(scores) / len(scores) if scores else 0.5


def should_spawn_new_agent(team_state: TeamState) -> Tuple[bool, Optional[str]]:
    """
    Determine if we should hire a new agent based on performance.
    
    Returns:
        (should_spawn, reason)
    """
    dims_mean = team_state.score_history.dims_mean
    avg_overall_history = team_state.score_history.avg_overall
    
    # Check cooldown
    if team_state.iteration < SPAWN_COOLDOWN:
        return False, None
    
    # Check if team is at capacity
    if len(team_state.agents) >= TEAM_CAP:
        return False, None
    
    # Check overall performance
    if avg_overall_history:
        current_overall = avg_overall_history[-1]
        if current_overall < WEAK_OVERALL_THRESHOLD:
            return True, f"avg_overall={current_overall:.2f} < {WEAK_OVERALL_THRESHOLD}"
    
    # Check weakest dimension
    if dims_mean:
        weakest_dim, weakest_score = get_weakest_dimension(dims_mean)
        if weakest_score < WEAK_DIM_THRESHOLD:
            return True, f"{weakest_dim}={weakest_score:.2f} < {WEAK_DIM_THRESHOLD}"
    
    return False, None


def generate_hire_plan(team_state: TeamState) -> List[HirePlan]:
    """
    Generate hiring recommendations based on team weaknesses.
    
    If team is empty (bootstrap scenario), use LLM to ideate initial team.
    Otherwise, evaluate performance and hire specialists as needed.
    """
    # BOOTSTRAP: Empty team → Use LLM to ideate initial team
    if len(team_state.agents) == 0:
        from hr_validation_agent.llm_ideation import ideate_initial_team
        
        print("[INFO] Empty team detected. Using LLM to ideate initial team composition...")
        print(f"[INFO] Project Goal: {team_state.project_goal}")
        print(f"[INFO] Target Audience: {team_state.target_audience}")
        print(f"[INFO] Content Focus: {team_state.content_focus}")
        
        # Pass context to LLM for ideation
        initial_roles = ideate_initial_team(
            project_goal=team_state.project_goal,
            target_audience=team_state.target_audience,
            content_focus=team_state.content_focus,
            failures=team_state.failures
        )
        
        # Update core_roles based on LLM's is_core flags
        core_role_names = [role["name"] for role in initial_roles if role.get("is_core", False)]
        if core_role_names:
            # Note: team_state is immutable, so we just use this for logging
            print(f"[INFO] Suggested core roles: {core_role_names}")
        
        return [
            HirePlan(
                name=role["name"],
                role=role["role"],
                system_prompt=role["prompt"],
                reason=f"Bootstrap: {role['reason']}"
            )
            for role in initial_roles
        ]
    
    # NORMAL OPERATION: Evaluate existing team and use LLM to design specialist
    should_spawn, reason = should_spawn_new_agent(team_state)
    if not should_spawn:
        return []
    
    dims_mean = team_state.score_history.dims_mean
    weakest_dim, weakest_score = get_weakest_dimension(dims_mean)
    
    # Build team context for LLM
    team_context = {agent.name: agent.role for agent in team_state.agents}
    
    # Use LLM to design specialist for the weakness
    from hr_validation_agent.llm_ideation import ideate_specialist_for_weakness
    
    print(f"[INFO] Team weakness detected: {weakest_dim}={weakest_score:.2f}")
    print(f"[INFO] Using LLM to design specialist to improve {weakest_dim}...")
    
    specialist = ideate_specialist_for_weakness(
        weakest_dimension=weakest_dim,
        current_score=weakest_score,
        team_context=team_context,
        project_goal=team_state.project_goal
    )
    
    hire = HirePlan(
        name=specialist["name"],
        role=specialist["role"],
        system_prompt=specialist["prompt"],
        reason=f"Addressing weakness: {reason}. {specialist['reason']}"
    )
    
    return [hire]


def identify_merge_candidates(team_state: TeamState) -> List[MergePlan]:
    """
    Find pairs of agents with high similarity that should be merged.
    Returns at most 1 merge suggestion per iteration.
    """
    agents = team_state.agents
    merge_candidates = []
    
    for agent in agents:
        for other_name, similarity in agent.prompt_similarity.items():
            if similarity > SIM_THRESHOLD:
                # Find the other agent
                other_agent = next((a for a in agents if a.name == other_name), None)
                if other_agent and agent.role == other_agent.role:
                    # Avoid duplicate pairs
                    if agent.name < other_name:  # lexicographic order
                        merge_candidates.append((agent.name, other_name, similarity))
    
    # Return only the most similar pair
    if merge_candidates:
        merge_candidates.sort(key=lambda x: x[2], reverse=True)
        top = merge_candidates[0]
        return [MergePlan(
            a=top[0],
            b=top[1],
            reason=f"High prompt similarity ({top[2]:.2f}) and overlapping roles. Consolidate to reduce redundancy."
        )]
    
    return []


def identify_prune_candidates(team_state: TeamState) -> List[PruneItem]:
    """
    Identify agents that should be removed due to low utility.
    """
    prune_list = []
    
    for agent in team_state.agents:
        # Never prune core roles
        if agent.role in team_state.core_roles or agent.name in team_state.core_roles:
            continue
        
        # Prune if utility below floor
        if agent.utility < UTILITY_FLOOR:
            prune_list.append(PruneItem(
                name=agent.name,
                reason=f"Utility {agent.utility:.2f} < floor {UTILITY_FLOOR}. Not a core role. Recommend removal."
            ))
    
    return prune_list


def generate_prompt_feedback(team_state: TeamState) -> List[PromptFeedback]:
    """
    Generate coaching suggestions for underperforming agents.
    """
    feedback_list = []
    team_mean = get_team_mean_overall(team_state.agents)
    
    for agent in team_state.agents:
        agent_overall = agent.last_scores.get("overall", 0.5)
        
        if agent_overall < team_mean - UNDERPERFORMER_MARGIN:
            # Generate concrete coaching
            suggestion = (
                f"Agent '{agent.name}' is underperforming (score {agent_overall:.2f} vs team mean {team_mean:.2f}). "
                f"Suggestions: "
                f"1) Add 2 concrete rules to improve clarity and focus. "
                f"2) Include 1 positive example of desired output style. "
                f"3) Emphasize key dimension: {_get_weakest_agent_dim(agent)}."
            )
            
            feedback_list.append(PromptFeedback(
                agent=agent.name,
                suggestion=suggestion
            ))
    
    return feedback_list


def _get_weakest_agent_dim(agent: AgentState) -> str:
    """Helper to find agent's weakest dimension."""
    scores = {k: v for k, v in agent.last_scores.items() if k != "overall"}
    if not scores:
        return "clarity"
    return min(scores.items(), key=lambda x: x[1])[0]

