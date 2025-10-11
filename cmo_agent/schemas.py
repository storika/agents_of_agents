"""
CMO Agent 데이터 스키마
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ContentCandidate(BaseModel):
    """생성된 콘텐츠 후보"""
    text: str = Field(..., description="소셜 미디어 포스트 텍스트 (≤280자)")
    media_prompt: str = Field(..., description="미디어 생성 프롬프트")
    mode: str = Field(default="image", description="미디어 타입: image, video, gif")
    scores: Optional[Dict[str, float]] = Field(default=None, description="평가 점수")
    
    def calculate_overall_score(self) -> float:
        """종합 점수 계산"""
        if not self.scores:
            return 0.0
        
        weights = {
            "clarity": 0.25,
            "novelty": 0.25,
            "shareability": 0.30,
            "credibility": 0.10,
            "safety": 0.10
        }
        
        overall = sum(
            self.scores.get(metric, 0.0) * weight 
            for metric, weight in weights.items()
        )
        
        return round(overall, 2)


class EvaluationScores(BaseModel):
    """평가 점수"""
    clarity: float = Field(ge=0.0, le=1.0, description="명확성 점수")
    novelty: float = Field(ge=0.0, le=1.0, description="참신성 점수")
    shareability: float = Field(ge=0.0, le=1.0, description="공유 가능성 점수")
    credibility: float = Field(ge=0.0, le=1.0, description="신뢰도 점수")
    safety: float = Field(ge=0.0, le=1.0, description="안전성 점수")
    overall: float = Field(ge=0.0, le=1.0, description="종합 점수")


class SelectedContent(BaseModel):
    """선택된 최종 콘텐츠"""
    text: str
    media_prompt: str
    mode: str
    expected_overall: float


class CMOOutput(BaseModel):
    """CMO 실행 결과"""
    iteration: int = Field(default=0, description="현재 반복 횟수")
    candidates: List[Dict[str, Any]] = Field(default_factory=list, description="생성된 후보들")
    selected: Optional[SelectedContent] = Field(default=None, description="선택된 콘텐츠")
    publish_status: str = Field(default="pending", description="발행 상태: pending, queued, published, failed")
    feedback_summary: str = Field(default="", description="피드백 요약")
    
    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return self.model_dump_json(indent=2)


class ResearchResult(BaseModel):
    """리서치 결과"""
    topics: List[str] = Field(default_factory=list, description="트렌딩 토픽")
    keywords: List[str] = Field(default_factory=list, description="인기 키워드")
    tone_style: str = Field(default="conversational", description="권장 톤/스타일")
    insights: str = Field(default="", description="인사이트")


class TeamState(BaseModel):
    """팀 상태"""
    iteration: int = Field(default=0)
    active_agents: List[Dict[str, Any]] = Field(default_factory=list)
    last_metrics: Optional[Dict[str, float]] = Field(default=None)


class IterationMetrics(BaseModel):
    """반복 메트릭"""
    iteration: int
    selected_candidate: Dict[str, Any]
    predicted_score: float
    actual_engagement: Optional[Dict[str, int]] = Field(default=None)
    timestamp: str


# ===== NEW LAYER SCHEMAS =====

class TrendingTopic(BaseModel):
    """트렌딩 토픽"""
    topic_name: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    timeliness_score: float = Field(ge=0.0, le=1.0)


class ViralAngle(BaseModel):
    """바이럴 가능성이 있는 각도"""
    angle_summary: str
    potential_platforms: List[str]
    engagement_likelihood: float = Field(ge=0.0, le=1.0)


class ResearchLayerOutput(BaseModel):
    """Research Layer 출력"""
    trending_topics: List[TrendingTopic]
    audience_insights: str
    viral_potential_angles: List[ViralAngle]
    data_sources_used: List[str]


class ContentIdea(BaseModel):
    """콘텐츠 아이디어"""
    idea_id: str
    title: str
    hook: str
    angle: str
    target_platforms: List[str]
    novelty_score: float = Field(ge=0.0, le=1.0)
    creativity_score: float = Field(ge=0.0, le=1.0)
    engagement_potential_score: float = Field(ge=0.0, le=1.0)


class CreativeWriterOutput(BaseModel):
    """Creative Writer Layer 출력"""
    ideas: List[ContentIdea]


class ContentPiece(BaseModel):
    """생성된 콘텐츠 조각"""
    platform: str
    format: str
    content: str
    character_count: int
    hashtags: List[str]
    call_to_action: Optional[str] = None
    clarity_score: float = Field(ge=0.0, le=1.0)
    shareability_score: float = Field(ge=0.0, le=1.0)


class GeneratorOutput(BaseModel):
    """Generator Layer 출력"""
    generated_content_id: str
    source_idea_id: str
    content_pieces: List[ContentPiece]
    completeness_assessment: str


class ContentEvaluation(BaseModel):
    """콘텐츠 평가"""
    platform: str
    content_summary: str
    accuracy_score: float = Field(ge=0.0, le=1.0)
    objectivity_score: float = Field(ge=0.0, le=1.0)
    thoroughness_score: float = Field(ge=0.0, le=1.0)
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    feedback_points: List[str]


class CriticOutput(BaseModel):
    """Critic Layer 출력"""
    evaluation_id: str
    generated_content_id: str
    evaluations: List[ContentEvaluation]


class RedFlag(BaseModel):
    """안전성 위험 플래그"""
    category: str  # 'Brand Safety', 'Ethical', 'Legal'
    description: str
    severity: str  # 'minor', 'moderate', 'severe'


class SafetyOutput(BaseModel):
    """Safety Layer 출력"""
    safety_assessment_id: str
    generated_content_id: str
    overall_safety_score: float = Field(ge=0.0, le=1.0)
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    compliance_status: str  # 'compliant', 'non-compliant', 'review_required'
    red_flags: List[RedFlag]
    recommendations: List[str]

