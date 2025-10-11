"""
Pydantic schemas for HR/Validation Agent input and output structures.
"""

from typing import Dict, List, Literal
from pydantic import BaseModel, Field


# ===== INPUT SCHEMAS =====

class AgentState(BaseModel):
    """Individual agent state in the team."""
    name: str
    role: str
    utility: float = Field(ge=0.0, le=1.0)  # EMA based on content they contributed to
    prompt_version: int = Field(ge=0)
    prompt_similarity: Dict[str, float] = Field(default_factory=dict)
    last_scores: Dict[str, float] = Field(default_factory=dict)  # Their evaluation scores (for critics) or content scores (for writers)


class ContentPerformance(BaseModel):
    """Performance data for a single piece of content."""
    content_id: str = Field(description="Unique content identifier")
    iteration: int = Field(description="When this content was created")
    contributors: List[str] = Field(description="Agents who contributed to this content")
    
    # Internal evaluation (from critic agents)
    internal_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Scores from critics: clarity, novelty, shareability, credibility, safety"
    )
    
    # External metrics (from Twitter, LinkedIn, Reddit, etc.)
    twitter_likes: int = Field(default=0)
    twitter_retweets: int = Field(default=0)
    twitter_replies: int = Field(default=0)
    linkedin_reactions: int = Field(default=0)
    linkedin_shares: int = Field(default=0)
    reddit_upvotes: int = Field(default=0)
    reddit_comments: int = Field(default=0)
    views: int = Field(default=0, description="Total impressions across platforms")
    click_through_rate: float = Field(default=0.0, ge=0, le=1)
    
    @property
    def engagement_rate(self) -> float:
        """Calculate overall engagement rate."""
        if self.views == 0:
            return 0.0
        total_engagement = (
            self.twitter_likes + self.twitter_retweets + self.twitter_replies +
            self.linkedin_reactions + self.linkedin_shares +
            self.reddit_upvotes + self.reddit_comments
        )
        return min(1.0, total_engagement / self.views)
    
    @property
    def viral_score(self) -> float:
        """Calculate viral score (0-1) based on shares/retweets."""
        shares = self.twitter_retweets + self.linkedin_shares
        if self.views == 0:
            return 0.0
        # Viral if >5% share rate
        return min(1.0, (shares / self.views) * 20)
    
    @property
    def overall_score(self) -> float:
        """Combine internal + external scores."""
        internal_avg = sum(self.internal_scores.values()) / len(self.internal_scores) if self.internal_scores else 0.5
        external_score = (self.engagement_rate + self.viral_score) / 2
        # Weight: 60% internal, 40% external
        return 0.6 * internal_avg + 0.4 * external_score


class ScoreHistory(BaseModel):
    """Historical performance scores."""
    avg_overall: List[float] = Field(default_factory=list)
    dims_mean: Dict[str, float] = Field(default_factory=dict)
    content_history: List[ContentPerformance] = Field(
        default_factory=list,
        description="Performance data for each piece of content (most recent first)"
    )


class TeamState(BaseModel):
    """Complete team state snapshot."""
    iteration: int = Field(ge=0)
    agents: List[AgentState]
    score_history: ScoreHistory
    failures: List[str] = Field(default_factory=list)
    core_roles: List[str] = Field(default_factory=lambda: ["HRValidation", "Explainer", "EngageCritic"])
    # Bootstrap context (for initial team ideation)
    project_goal: str = Field(
        default="Create engaging, high-quality content across multiple dimensions",
        description="High-level goal of the project/system"
    )
    target_audience: str = Field(
        default="General audience seeking informative and engaging content",
        description="Who is the content for?"
    )
    content_focus: str = Field(
        default="General topics with emphasis on clarity, novelty, and shareability",
        description="What kind of content should the team create?"
    )


# ===== OUTPUT SCHEMAS =====

class HirePlan(BaseModel):
    """Specification for hiring a new agent."""
    slot: str = Field(description="Slot identifier like 'writer/main', 'media/main', 'critic/main'")
    ref: str = Field(description="Archetype reference name from registry (e.g., 'Hooksmith', 'ImageComposer')")
    patch: Dict = Field(default_factory=dict, description="Modifications to archetype system_prompt")
    reason: str = Field(description="Numeric reason with metric threshold (e.g., 'shareability_mean < 0.55')")


class SwapPlan(BaseModel):
    """Specification for swapping an agent in a slot."""
    slot: str = Field(description="Slot identifier to swap")
    ref: str = Field(description="New archetype reference name")
    patch: Dict = Field(default_factory=dict, description="Modifications to archetype system_prompt")
    reason: str = Field(description="Numeric reason with metric threshold")


class MergePlan(BaseModel):
    """Specification for merging two agents."""
    slot: str = Field(description="Target slot for merged agent")
    from_agents: List[str] = Field(description="List of agent refs to merge", alias="from")
    to: str = Field(description="New merged agent reference name")
    patch: Dict = Field(default_factory=dict, description="Modifications to merged system_prompt")
    reason: str = Field(default="Agents too similar", description="Reason for merge")
    
    class Config:
        populate_by_name = True


class PruneItem(BaseModel):
    """Specification for pruning an agent."""
    slot: str = Field(description="Slot identifier to prune")
    reason: str = Field(description="Numeric reason (e.g., 'utility < 0.35 for 3 iters')")


class UpgradePlan(BaseModel):
    """Specification for upgrading an existing agent's prompt."""
    slot: str = Field(description="Slot identifier to upgrade")
    patch: Dict = Field(description="Modifications to system_prompt")
    reason: str = Field(default="Performance improvement", description="Reason for upgrade")


class PolicyUpdates(BaseModel):
    """HR operational policies and thresholds."""
    team_cap: int = Field(default=8, description="Maximum number of active agents")
    utility_floor: float = Field(default=0.35, description="Minimum utility to avoid pruning")
    sim_threshold: float = Field(default=0.8, description="Similarity threshold for merging")


class HRDecision(BaseModel):
    """Complete HR decision output (STRICT JSON)."""
    hire_plan: List[HirePlan] = Field(default_factory=list)
    swap_plan: List[SwapPlan] = Field(default_factory=list)
    merge_plan: List[MergePlan] = Field(default_factory=list)
    prune_list: List[PruneItem] = Field(default_factory=list)
    upgrade_plan: List[UpgradePlan] = Field(default_factory=list)
    policy_updates: PolicyUpdates = Field(default_factory=PolicyUpdates)

    def to_strict_json(self) -> str:
        """Export as strict JSON string."""
        return self.model_dump_json(indent=2, exclude_none=True, by_alias=True)

