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
    """Specification for hiring a new agent - ready to instantiate."""
    name: str
    role: Literal[
        "writer.specialist",      # Creates content (tweets, threads)
        "designer.specialist",    # Creates visuals, charts, memes  
        "critic.specialist",      # Evaluates quality before posting
        "analyzer.specialist",    # Analyzes trends, metrics, patterns
        "coordinator.specialist", # Orchestrates workflows, schedules
        "engager.specialist"      # Replies, networks, builds community
    ]
    system_prompt: str  # Complete ADK-compatible instruction
    reason: str
    
    # Agent instantiation config (ready to use)
    config: Dict = Field(
        default_factory=lambda: {
            "model": "gemini-2.5-flash",
            "temperature": 0.7,
            "max_tokens": 1024
        },
        description="LLM config for this agent"
    )
    tools: List[str] = Field(
        default_factory=list,
        description="Tool names this agent should have access to"
    )
    
    def to_agent_spec(self) -> Dict:
        """Convert to agent instantiation spec."""
        return {
            "name": self.name,
            "role": self.role,
            "instruction": self.system_prompt,
            "model": self.config["model"],
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 1024),
            "tools": self.tools,
            "metadata": {
                "hire_reason": self.reason,
                "created_by": "hr_validation_agent"
            }
        }


class MergePlan(BaseModel):
    """Specification for merging two agents."""
    a: str
    b: str
    reason: str


class PruneItem(BaseModel):
    """Specification for pruning an agent."""
    name: str
    reason: str


class PromptFeedback(BaseModel):
    """Feedback for improving an agent's prompt."""
    agent: str
    suggestion: str


class Policies(BaseModel):
    """HR operational policies and thresholds."""
    team_cap: int = 8
    utility_floor: float = 0.35
    sim_threshold: float = 0.80
    spawn_cooldown: int = 1


class HRDecision(BaseModel):
    """Complete HR decision output (STRICT JSON)."""
    hire_plan: List[HirePlan] = Field(default_factory=list)
    merge_plan: List[MergePlan] = Field(default_factory=list)
    prune_list: List[PruneItem] = Field(default_factory=list)
    prompt_feedback: List[PromptFeedback] = Field(default_factory=list)
    policies: Policies = Field(default_factory=Policies)

    def to_strict_json(self) -> str:
        """Export as strict JSON string."""
        return self.model_dump_json(indent=2, exclude_none=True)

