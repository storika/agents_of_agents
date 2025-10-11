"""
Weave 통합 - 에이전트 실행 및 콘텐츠 생성 추적
"""

import weave
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import json

load_dotenv()

# Initialize Weave
os.environ['WANDB_API_KEY'] = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
weave.init("mason-choi-storika/WeaveHacks2")


class WeaveAgent(weave.Model):
    """
    Weave-tracked Agent wrapper.
    모든 실행이 자동으로 Weave에 기록됩니다.
    """
    
    name: str
    role: str
    instruction: str
    model: str = "gemini-2.5-flash"
    
    @weave.op()
    def run(self, prompt: str) -> Dict[str, Any]:
        """
        에이전트 실행 (Weave가 자동으로 입력/출력 추적).
        
        Args:
            prompt: 에이전트에게 주는 프롬프트
        
        Returns:
            에이전트 응답 (딕셔너리)
        """
        # 실제 구현에서는 여기서 LLM 호출
        # 현재는 mock response
        return {
            "agent": self.name,
            "role": self.role,
            "response": f"[{self.name}] Processing: {prompt[:50]}...",
            "metadata": {
                "model": self.model,
                "prompt_length": len(prompt)
            }
        }


class ContentGenerationPipeline(weave.Model):
    """
    콘텐츠 생성 파이프라인 - Weave로 전체 과정 추적.
    """
    
    agents: Dict[str, WeaveAgent]
    config: Dict[str, Any]
    
    @weave.op()
    def generate_content(self, topic: str) -> Dict[str, Any]:
        """
        합의 기반 콘텐츠 생성 (Weave가 전체 프로세스 추적).
        
        Returns:
            {
                "content": "최종 콘텐츠",
                "iterations": 3,
                "scores": {...},
                "history": [...]
            }
        """
        history = []
        
        # Phase 1: Research
        context = self._gather_context(topic)
        history.append({"phase": "research", "context": context})
        
        # Phase 2: Iterative refinement
        content = None
        for i in range(1, self.config.get("max_iterations", 5) + 1):
            # Write
            content = self._write_round(content, context, i)
            
            # Evaluate
            scores = self._evaluate_round(content, i)
            
            history.append({
                "iteration": i,
                "content_preview": content[:100],
                "scores": scores
            })
            
            # Check consensus
            if scores["overall"] >= self.config.get("min_quality_score", 0.75):
                return {
                    "content": content,
                    "iterations": i,
                    "scores": scores,
                    "history": history,
                    "status": "success"
                }
        
        return {
            "content": content,
            "iterations": self.config.get("max_iterations", 5),
            "scores": scores,
            "history": history,
            "status": "max_iterations_reached"
        }
    
    @weave.op()
    def _gather_context(self, topic: str) -> Dict[str, Any]:
        """Phase 1: 컨텍스트 수집 (Weave 추적)"""
        context = {"topic": topic}
        
        # Analyzers 실행
        for name, agent in self.agents.items():
            if "analyzer" in agent.role or "scout" in name.lower():
                result = agent.run(f"Analyze context for: {topic}")
                context[name] = result
        
        return context
    
    @weave.op()
    def _write_round(self, previous_content: Optional[str], context: Dict, iteration: int) -> str:
        """Phase 2: 작성 라운드 (Weave 추적)"""
        writers = [a for a in self.agents.values() if "writer" in a.role]
        
        if not writers:
            return "No writers available"
        
        # 첫 번째 writer 사용
        writer = writers[0]
        prompt = f"Round {iteration}: Create content for {context['topic']}"
        
        if previous_content:
            prompt += f"\n\nPrevious: {previous_content}"
        
        result = writer.run(prompt)
        return result.get("response", "")
    
    @weave.op()
    def _evaluate_round(self, content: str, iteration: int) -> Dict[str, float]:
        """Phase 2: 평가 라운드 (Weave 추적)"""
        critics = [a for a in self.agents.values() if "critic" in a.role]
        
        scores = {
            "clarity": 0.5,
            "novelty": 0.5,
            "shareability": 0.5,
            "credibility": 0.5,
            "safety": 1.0
        }
        
        # Critics 병렬 실행
        for critic in critics:
            result = critic.run(f"Evaluate: {content}")
            # Mock scoring
            if "clarity" in critic.name.lower():
                scores["clarity"] = 0.8
            elif "engage" in critic.name.lower():
                scores["shareability"] = 0.85
        
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores


class HRDecisionTracker(weave.Model):
    """
    HR 결정 추적 - Weave Dataset으로 저장.
    """
    
    project_name: str = "mason-choi-storika/WeaveHacks2"
    
    @weave.op()
    def log_hr_decision(
        self,
        iteration: int,
        team_state: Dict[str, Any],
        hr_decisions: Dict[str, Any]
    ):
        """
        HR 결정을 Weave에 기록.
        
        Args:
            iteration: Iteration 번호
            team_state: 팀 상태
            hr_decisions: HR 결정 (hire_plan, merge_plan, etc.)
        """
        # Weave에 자동으로 기록됨
        return {
            "iteration": iteration,
            "team_size": len(team_state.get("agents", [])),
            "decisions": {
                "hires": len(hr_decisions.get("hire_plan", [])),
                "merges": len(hr_decisions.get("merge_plan", [])),
                "prunes": len(hr_decisions.get("prune_list", [])),
                "coaches": len(hr_decisions.get("prompt_feedback", []))
            },
            "hire_details": hr_decisions.get("hire_plan", []),
            "team_performance": team_state.get("score_history", {})
        }
    
    @weave.op()
    def log_content_performance(
        self,
        content_id: str,
        content: str,
        internal_scores: Dict[str, float],
        external_metrics: Dict[str, int]
    ):
        """
        콘텐츠 성과를 Weave에 기록.
        """
        return {
            "content_id": content_id,
            "content_preview": content[:200],
            "internal_scores": internal_scores,
            "external_metrics": external_metrics,
            "engagement_rate": (
                external_metrics.get("twitter_likes", 0) + 
                external_metrics.get("twitter_retweets", 0)
            ) / max(external_metrics.get("views", 1), 1)
        }


# 사용 예시
if __name__ == "__main__":
    print("🐝 Weave Integration 테스트")
    print("=" * 70)
    
    # 1. Weave Agent 생성
    agents = {
        "Hooksmith": WeaveAgent(
            name="Hooksmith",
            role="writer.specialist",
            instruction="Create viral hooks",
            model="gemini-2.5-flash"
        ),
        "ClarityChecker": WeaveAgent(
            name="ClarityChecker",
            role="critic.specialist",
            instruction="Evaluate clarity",
            model="gemini-2.5-flash"
        )
    }
    
    # 2. 콘텐츠 생성 (Weave 추적)
    pipeline = ContentGenerationPipeline(
        agents=agents,
        config={
            "max_iterations": 3,
            "min_quality_score": 0.75
        }
    )
    
    result = pipeline.generate_content("WeaveHack2 progress update")
    
    print(f"\n✅ Content generated!")
    print(f"Iterations: {result['iterations']}")
    print(f"Status: {result['status']}")
    print(f"Final score: {result['scores']['overall']:.2f}")
    
    # 3. HR 결정 추적
    tracker = HRDecisionTracker()
    
    hr_log = tracker.log_hr_decision(
        iteration=1,
        team_state={"agents": agents},
        hr_decisions={"hire_plan": [], "merge_plan": []}
    )
    
    print(f"\n✅ HR decision logged to Weave")
    
    # 4. 콘텐츠 성과 추적
    perf_log = tracker.log_content_performance(
        content_id="tweet_001",
        content=result["content"],
        internal_scores=result["scores"],
        external_metrics={
            "twitter_likes": 180,
            "twitter_retweets": 12,
            "views": 2100
        }
    )
    
    print(f"✅ Content performance logged to Weave")
    print(f"Engagement rate: {perf_log['engagement_rate']:.1%}")
    
    print(f"\n🌐 View in Weave: https://wandb.ai/mason-choi-storika/WeaveHacks2/weave")

