"""
Pydantic schemas for Prompt Optimizer (5-layer architecture)
"""

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# ===== INPUT SCHEMAS =====

class LayerState(BaseModel):
    """State for one of the 5 fixed layers."""
    layer_id: Literal["research", "creative_writer", "generator", "critic", "safety"]
    layer_name: str
    current_prompt: str
    prompt_version: int = Field(ge=0, default=0)
    metrics: Dict[str, float] = Field(default_factory=dict)  # Layer-specific metrics
    performance_history: List[float] = Field(default_factory=list)  # Historical average scores


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


class PerformanceMetrics(BaseModel):
    """Overall system performance metrics."""
    iteration: int = Field(ge=0)
    overall_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="System-wide metrics: clarity, novelty, shareability, credibility, safety, overall"
    )
    layers: Dict[str, LayerState] = Field(
        default_factory=dict,
        description="Performance data for each of the 5 layers"
    )
    content_history: List[ContentPerformance] = Field(
        default_factory=list,
        description="Recent content performance (most recent first)"
    )
    failures: List[str] = Field(default_factory=list, description="Recent errors or issues")


# ===== OUTPUT SCHEMAS =====

class PromptUpdate(BaseModel):
    """Complete new prompt for a layer (replaces old prompt entirely)."""
    layer: Literal["research", "creative_writer", "generator", "critic", "safety"]
    new_prompt: str = Field(description="Complete system prompt that will replace the old one")
    reason: str = Field(description="Why this layer needs improvement (e.g., 'shareability 0.48 < 0.55; engagement 0%')")
    expected_impact: str = Field(description="Quantitative prediction of improvement (e.g., 'increase shareability by 0.15+; boost engagement to 2-5%')")


class GlobalAdjustments(BaseModel):
    """System-wide configuration adjustments."""
    target_audience_update: Optional[str] = None
    brand_voice: Optional[str] = None
    topics_to_avoid: List[str] = Field(default_factory=list)


class PerformanceThresholds(BaseModel):
    """Metric thresholds for evaluation."""
    clarity: float = Field(default=0.55, ge=0, le=1)
    novelty: float = Field(default=0.55, ge=0, le=1)
    shareability: float = Field(default=0.55, ge=0, le=1)
    credibility: float = Field(default=0.60, ge=0, le=1)
    safety: float = Field(default=0.80, ge=0, le=1)


class PromptOptimizationDecision(BaseModel):
    """Complete prompt optimization output (STRICT JSON)."""
    prompts: List[PromptUpdate] = Field(
        default_factory=list,
        description="List of complete new prompts (5 for bootstrap, 1-3 for improvements)"
    )
    thresholds: PerformanceThresholds = Field(
        default_factory=PerformanceThresholds,
        description="Updated performance thresholds"
    )
    global_adjustments: GlobalAdjustments = Field(
        default_factory=GlobalAdjustments,
        description="System-wide configuration updates (optional)"
    )

    def to_strict_json(self) -> str:
        """Export as strict JSON string."""
        return self.model_dump_json(indent=2, exclude_none=True)

