# 🔄 콘텐츠 생성 Iteration 전략

## 문제: 에이전트들이 어떻게 협업할까?

### 옵션 1: 한 번씩 실행 (One-Shot)
```
TrendScout → ViralHook → ContentCrafter → EngageCritic → 발행
```
- 장점: 빠름, 간단함
- 단점: 품질 보장 어려움, 피드백 반영 불가

### 옵션 2: 합의 기반 반복 (Consensus-Based Iteration) ⭐ 권장
```
Round 1: Writers 작성 → Critics 평가 (점수: 0.58)
Round 2: Writers 수정 → Critics 재평가 (점수: 0.72)
Round 3: Writers 최종 수정 → Critics 재평가 (점수: 0.83) ✅ 발행
```
- 장점: 높은 품질, 피드백 반영, 실제 토론처럼 작동
- 단점: 느림 (하지만 품질이 더 중요!)

---

## ✅ 권장: Multi-Turn Refinement with Consensus

**컨셉**: 에이전트들이 **품질 기준을 만족할 때까지** 여러 번 토론하고 개선

### 프로세스

```python
MAX_ITERATIONS = 5  # 무한 루프 방지
MIN_QUALITY_SCORE = 0.75  # 발행 임계값

def generate_content_with_consensus(agents, topic):
    """
    에이전트들이 합의에 도달할 때까지 반복.
    
    Returns:
        content: 최종 콘텐츠
        iterations: 걸린 라운드 수
        final_score: 최종 품질 점수
    """
    
    # Phase 1: 아이디어 수집 (Parallel)
    trends = agents["TrendScout"].run(f"Analyze trends for: {topic}")
    ideas = agents["Ideator"].run(f"Brainstorm angles for: {topic}")
    
    # Phase 2: 반복적 개선 (Iterative Refinement)
    content = None
    scores = None
    
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== Round {iteration} ===")
        
        # Writers가 작성/수정
        if iteration == 1:
            # 첫 번째: 초안 작성
            hook = agents["ViralHook"].run(
                f"Create viral hook for: {ideas['best_angle']}"
            )
            body = agents["ContentCrafter"].run(
                f"Write content with hook: {hook}, trend: {trends['top_topic']}"
            )
            content = f"{hook}\n\n{body}"
        else:
            # 이후: 피드백 기반 수정
            content = agents["ContentCrafter"].run(
                f"Improve this content based on feedback:\n"
                f"Content: {content}\n"
                f"Feedback: {scores['feedback']}"
            )
        
        # Critics가 평가 (Parallel)
        clarity_score = agents["ClarityChecker"].run(f"Evaluate clarity: {content}")
        engage_score = agents["EngageCritic"].run(f"Evaluate engagement: {content}")
        safety_check = agents["HRValidation"].run(f"Check safety: {content}")
        
        # 종합 점수 계산
        scores = {
            "clarity": clarity_score["score"],
            "novelty": engage_score["novelty"],
            "shareability": engage_score["shareability"],
            "credibility": engage_score["credibility"],
            "safety": safety_check["score"],
            "overall": (
                clarity_score["score"] * 0.2 +
                engage_score["novelty"] * 0.2 +
                engage_score["shareability"] * 0.3 +
                engage_score["credibility"] * 0.2 +
                safety_check["score"] * 0.1
            ),
            "feedback": [
                clarity_score.get("feedback", ""),
                engage_score.get("feedback", ""),
            ]
        }
        
        print(f"Overall Score: {scores['overall']:.2f}")
        
        # 합의 체크: 기준 통과?
        if scores["overall"] >= MIN_QUALITY_SCORE:
            print(f"✅ Consensus reached! Publishing after {iteration} rounds.")
            return content, iteration, scores
        
        # 안전성 실패하면 즉시 중단
        if scores["safety"] < 0.9:
            print(f"❌ Safety violation! Aborting.")
            return None, iteration, scores
        
        print(f"⚠️ Quality below threshold. Refining...")
    
    # 최대 반복 도달
    print(f"⏰ Max iterations reached. Using best attempt.")
    return content, MAX_ITERATIONS, scores
```

---

## 🎯 실전 예시

### Iteration 1 (초안)

```
[TrendScout] "AI agents are trending, WeaveHack2 getting attention"
[Ideator] "Angle: behind-the-scenes of building agents"
[ViralHook] "Everyone thinks building AI agents is hard. It's not."
[ContentCrafter] "Everyone thinks building AI agents is hard. It's not.
                 Here's what I learned building a multi-agent system
                 for WeaveHack2 👇"
                 
[ClarityChecker] Score: 0.75 "Clear but generic"
[EngageCritic] Score: 0.68 (novelty: 0.60, shareability: 0.70)
                "Feedback: Hook is good but body is weak. Add specifics."
[HRValidation] Score: 1.0 "Safe"

Overall: 0.71 ❌ Below 0.75 threshold
```

### Iteration 2 (개선)

```
[ContentCrafter] (피드백 반영)
"Everyone thinks building AI agents is hard. It's not.

I built a self-optimizing agent team for WeaveHack2.
The HR agent fires/hires other agents based on performance.

3 viral tweets later, here's what worked:
- Trend analyzer that scans Twitter every 2 hours
- Contrarian writer that challenges AI hype
- Critic that rejects 70% of drafts

The twist? The agents improved THEMSELVES. 
No human intervention for 48 hours. 🤯"

[ClarityChecker] Score: 0.85 "Much clearer, specific examples"
[EngageCritic] Score: 0.82 (novelty: 0.80, shareability: 0.85)
                "Feedback: Strong! Maybe add a surprising stat?"
[HRValidation] Score: 1.0 "Safe"

Overall: 0.83 ✅ Passes threshold!
```

---

## 🔧 구현: content_generator.py

```python
from typing import Dict, Tuple, Optional
import json

class ContentGenerator:
    def __init__(self, agents: Dict, config: Dict = None):
        self.agents = agents
        self.config = config or {
            "max_iterations": 5,
            "min_quality_score": 0.75,
            "min_safety_score": 0.9
        }
    
    def generate(self, topic: str) -> Tuple[Optional[str], int, Dict]:
        """
        합의 기반 콘텐츠 생성.
        
        Returns:
            (content, iterations, scores)
        """
        # Phase 1: Research (Parallel)
        context = self._gather_context(topic)
        
        # Phase 2: Iterative Refinement
        content = None
        scores = None
        
        for i in range(1, self.config["max_iterations"] + 1):
            # Write
            content = self._write_content(content, context, scores, iteration=i)
            
            # Evaluate
            scores = self._evaluate_content(content)
            
            # Check consensus
            if self._is_consensus_reached(scores):
                return content, i, scores
            
            if scores["safety"] < self.config["min_safety_score"]:
                return None, i, scores
        
        return content, self.config["max_iterations"], scores
    
    def _gather_context(self, topic: str) -> Dict:
        """Phase 1: 병렬로 컨텍스트 수집"""
        context = {}
        
        if "TrendScout" in self.agents:
            context["trends"] = self.agents["TrendScout"].run(
                f"Analyze Twitter trends for: {topic}"
            )
        
        if "Ideator" in self.agents:
            context["ideas"] = self.agents["Ideator"].run(
                f"Brainstorm angles for: {topic}"
            )
        
        return context
    
    def _write_content(
        self, 
        previous_content: Optional[str],
        context: Dict,
        scores: Optional[Dict],
        iteration: int
    ) -> str:
        """Phase 2: 작성 또는 수정"""
        
        if iteration == 1:
            # 첫 번째: 초안
            prompt = f"""Create a viral tweet about: {context.get('topic', 'WeaveHack2')}
            
Trends: {context.get('trends', {})}
Ideas: {context.get('ideas', {})}

Make it attention-grabbing and specific."""
        else:
            # 이후: 피드백 반영
            prompt = f"""Improve this content based on critic feedback:

Content:
{previous_content}

Feedback:
{json.dumps(scores.get('feedback', {}), indent=2)}

Overall score: {scores.get('overall', 0):.2f} (target: {self.config['min_quality_score']})

Make specific improvements to address the feedback."""
        
        # Writers 실행 (순차 또는 병렬)
        if "ContentCrafter" in self.agents:
            return self.agents["ContentCrafter"].run(prompt)
        
        return previous_content or "Fallback content"
    
    def _evaluate_content(self, content: str) -> Dict:
        """Phase 2: Critics가 병렬 평가"""
        scores = {
            "clarity": 0.5,
            "novelty": 0.5,
            "shareability": 0.5,
            "credibility": 0.5,
            "safety": 1.0,
            "feedback": []
        }
        
        # 각 critic 병렬 실행
        if "ClarityChecker" in self.agents:
            clarity_result = self.agents["ClarityChecker"].run(
                f"Evaluate clarity of: {content}"
            )
            scores["clarity"] = clarity_result.get("score", 0.5)
            scores["feedback"].append(clarity_result.get("feedback", ""))
        
        if "EngageCritic" in self.agents:
            engage_result = self.agents["EngageCritic"].run(
                f"Evaluate engagement of: {content}"
            )
            scores["novelty"] = engage_result.get("novelty", 0.5)
            scores["shareability"] = engage_result.get("shareability", 0.5)
            scores["credibility"] = engage_result.get("credibility", 0.5)
            scores["feedback"].append(engage_result.get("feedback", ""))
        
        if "HRValidation" in self.agents:
            safety_result = self.agents["HRValidation"].run(
                f"Check safety of: {content}"
            )
            scores["safety"] = safety_result.get("score", 1.0)
        
        # Overall 계산
        scores["overall"] = (
            scores["clarity"] * 0.2 +
            scores["novelty"] * 0.2 +
            scores["shareability"] * 0.3 +
            scores["credibility"] * 0.2 +
            scores["safety"] * 0.1
        )
        
        return scores
    
    def _is_consensus_reached(self, scores: Dict) -> bool:
        """합의 도달 체크"""
        return (
            scores["overall"] >= self.config["min_quality_score"] and
            scores["safety"] >= self.config["min_safety_score"]
        )


# 사용 예시
if __name__ == "__main__":
    from agent_factory import apply_hr_decisions, load_team_state
    from hr_validation_agent.agent import analyze_team_and_decide
    import json
    
    # 1. 에이전트 팀 생성
    team_state = load_team_state("examples/mason_weavehack2_empty.json")
    result = analyze_team_and_decide(json.dumps(team_state))
    hr_decisions = json.loads(result)
    
    agents = {}
    agents = apply_hr_decisions(agents, hr_decisions)
    
    # 2. 콘텐츠 생성 (합의 기반)
    generator = ContentGenerator(agents, {
        "max_iterations": 5,
        "min_quality_score": 0.75,
        "min_safety_score": 0.9
    })
    
    content, iterations, scores = generator.generate(
        topic="Building self-optimizing agents for WeaveHack2"
    )
    
    print(f"\n✅ Content ready after {iterations} rounds!")
    print(f"📊 Final score: {scores['overall']:.2f}")
    print(f"\n📝 Content:\n{content}")
```

---

## 📊 성능 vs 품질 Trade-off

| 전략 | 속도 | 품질 | 피드백 반영 | 권장 사용 |
|------|------|------|-------------|----------|
| **One-Shot** | ⚡⚡⚡ 빠름 | ⭐⭐ 보통 | ❌ 없음 | 빠른 테스트 |
| **Fixed Rounds** (3회) | ⚡⚡ 적당 | ⭐⭐⭐ 좋음 | ✅ 제한적 | 일반적 상황 |
| **Consensus-Based** | ⚡ 느림 | ⭐⭐⭐⭐ 매우 좋음 | ✅✅ 완전 | 바이럴 목표 ⭐ |

**Mason의 경우**: 바이럴이 목표이므로 **Consensus-Based** 권장!

---

## 🎯 핵심 포인트

1. **품질 > 속도**: 바이럴 콘텐츠는 1개만 있어도 충분
2. **피드백 루프**: Critics의 피드백을 반영해야 개선됨
3. **안전장치**: MAX_ITERATIONS로 무한 루프 방지
4. **명확한 기준**: MIN_QUALITY_SCORE로 합의 정의
5. **병렬 실행**: Context 수집과 평가는 병렬로

---

**버전**: 1.0.0  
**업데이트**: 2025-10-11

