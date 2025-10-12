"""
합의 기반 콘텐츠 생성 시스템
"""

from typing import Dict, Tuple, Optional, Any
import json
import weave


class ContentGenerator:
    """
    Multi-turn refinement with consensus.
    에이전트들이 품질 기준을 만족할 때까지 반복적으로 개선.
    """
    
    def __init__(self, agents: Dict[str, Any], config: Dict = None):
        """
        Args:
            agents: {name: Agent} 딕셔너리
            config: {
                "max_iterations": 5,
                "min_quality_score": 0.75,
                "min_safety_score": 0.9
            }
        """
        self.agents = agents
        self.config = config or {
            "max_iterations": 5,
            "min_quality_score": 0.75,
            "min_safety_score": 0.9
        }
    
    @weave.op()
    def generate(self, topic: str, verbose: bool = True) -> Tuple[Optional[str], int, Dict]:
        """
        합의 기반 콘텐츠 생성.
        
        Args:
            topic: 콘텐츠 주제
            verbose: 로그 출력 여부
        
        Returns:
            (content, iterations, scores)
            - content: 최종 콘텐츠 (or None if failed)
            - iterations: 걸린 라운드 수
            - scores: 최종 점수 딕셔너리
        """
        if verbose:
            print(f"\n🎨 콘텐츠 생성 시작: {topic}")
            print("=" * 70)
        
        # Phase 1: Research & Context Gathering
        context = self._gather_context(topic, verbose)
        
        # Phase 2: Iterative Refinement
        content = None
        scores = None
        
        for i in range(1, self.config["max_iterations"] + 1):
            if verbose:
                print(f"\n{'='*70}")
                print(f"Round {i}/{self.config['max_iterations']}")
                print(f"{'='*70}")
            
            # Write/Revise
            content = self._write_content(content, context, scores, iteration=i, verbose=verbose)
            
            if verbose:
                print(f"\n📝 Content ({len(content)} chars):")
                print(content[:200] + "..." if len(content) > 200 else content)
            
            # Evaluate
            scores = self._evaluate_content(content, verbose)
            
            if verbose:
                print(f"\n📊 Scores:")
                for key, val in scores.items():
                    if key != "feedback":
                        print(f"  {key}: {val:.2f}")
            
            # Check consensus
            if self._is_consensus_reached(scores):
                if verbose:
                    print(f"\n✅ Consensus reached after {i} rounds!")
                    print(f"Overall: {scores['overall']:.2f} >= {self.config['min_quality_score']}")
                return content, i, scores
            
            # Safety check
            if scores["safety"] < self.config["min_safety_score"]:
                if verbose:
                    print(f"\n❌ Safety violation! Aborting.")
                return None, i, scores
            
            if verbose:
                print(f"\n⚠️  Quality: {scores['overall']:.2f} < {self.config['min_quality_score']}")
                print(f"Refining based on feedback...")
        
        # Max iterations reached
        if verbose:
            print(f"\n⏰ Max iterations reached. Using best attempt.")
        return content, self.config["max_iterations"], scores
    
    @weave.op()
    def _gather_context(self, topic: str, verbose: bool) -> Dict:
        """Phase 1: 병렬로 컨텍스트 수집"""
        if verbose:
            print(f"\n🔍 Phase 1: Gathering context...")
        
        context = {"topic": topic}
        
        # Analyzer agents (trends, ideas, etc.)
        if "TrendScout" in self.agents:
            if verbose:
                print("  - TrendScout analyzing trends...")
            # Mock response (실제로는 agent.run() 호출)
            context["trends"] = {
                "top_topic": "AI agents trending",
                "sentiment": "positive",
                "engagement_potential": 0.85
            }
        
        if "Ideator" in self.agents:
            if verbose:
                print("  - Ideator brainstorming angles...")
            context["ideas"] = {
                "best_angle": "Behind-the-scenes of building agents",
                "alternatives": ["Contrarian take", "Tutorial", "Results showcase"]
            }
        
        return context
    
    @weave.op()
    def _write_content(
        self,
        previous_content: Optional[str],
        context: Dict,
        scores: Optional[Dict],
        iteration: int,
        verbose: bool
    ) -> str:
        """Phase 2: 작성 또는 수정"""
        
        if iteration == 1:
            # 첫 번째: 초안 작성
            prompt = f"""Create a viral tweet about: {context['topic']}

Context:
- Trends: {json.dumps(context.get('trends', {}), indent=2)}
- Ideas: {json.dumps(context.get('ideas', {}), indent=2)}

Requirements:
- Attention-grabbing hook
- Specific examples
- Under 280 characters or thread format
- End with a call-to-action or cliffhanger"""
            
            # 🎯 Weave Prompt로 publish (Round 1)
            try:
                prompt_obj = weave.StringPrompt(prompt)
                weave.publish(prompt_obj, name="content_generation_prompt")
                print(f"📝 Prompt published: Round {iteration} (Initial Draft)")
            except Exception as e:
                print(f"⚠️  Failed to publish prompt: {e}")
                import traceback
                traceback.print_exc()
            
            if verbose:
                print(f"\n✍️  Writers creating initial draft...")
        
        else:
            # 이후: 피드백 기반 수정
            feedback_str = "\n".join(f"- {f}" for f in scores.get("feedback", []) if f)
            
            prompt = f"""Improve this content based on critic feedback:

Current Content:
{previous_content}

Feedback:
{feedback_str}

Current Score: {scores.get('overall', 0):.2f} / Target: {self.config['min_quality_score']}

Make specific improvements to raise the score."""
            
            # 🎯 Weave Prompt로 publish (Round 2+)
            # 같은 이름으로 publish → 자동으로 새 버전 생성!
            try:
                with weave.attributes({
                    'round': iteration,
                    'topic': context.get('topic', 'unknown'),
                    'previous_score': scores.get('overall', 0),
                    'target_score': self.config['min_quality_score'],
                    'improvement_stage': 'refinement'
                }):
                    prompt_obj = weave.StringPrompt(prompt)
                    weave.publish(prompt_obj, name="content_generation_prompt")
                    print(f"📝 Prompt published: Round {iteration} (Refinement, Score: {scores.get('overall', 0):.2f})")
            except Exception as e:
                print(f"⚠️  Failed to publish prompt: {e}")
                import traceback
                traceback.print_exc()
            
            if verbose:
                print(f"\n✍️  Writers refining (Round {iteration})...")
        
        # Writers 실행
        writers = [name for name in self.agents.keys() if "writer" in self.agents[name].description.lower()]
        
        if writers:
            # 실제로는 agent.run(prompt) 호출
            # Mock response for demo
            if iteration == 1:
                content = """Everyone thinks building AI agents is hard. It's not.

I built a self-optimizing agent team for WeaveHack2.
The HR agent fires/hires other agents based on Twitter performance.

3 viral tweets later, here's what worked 👇

🧵"""
            else:
                content = previous_content + "\n\n[Improved based on feedback]"
            
            return content
        
        return previous_content or "No writers available."
    
    @weave.op()
    def _evaluate_content(self, content: str, verbose: bool) -> Dict:
        """Phase 2: Critics가 병렬 평가"""
        if verbose:
            print(f"\n🔍 Critics evaluating...")
        
        scores = {
            "clarity": 0.5,
            "novelty": 0.5,
            "shareability": 0.5,
            "credibility": 0.5,
            "safety": 1.0,
            "feedback": []
        }
        
        # Mock evaluation (실제로는 각 critic agent 실행)
        critics = [name for name in self.agents.keys() if "critic" in self.agents[name].description.lower()]
        
        if "ClarityChecker" in self.agents:
            scores["clarity"] = 0.85
            scores["feedback"].append("Good structure, clear message")
        
        if "EngageCritic" in self.agents:
            scores["novelty"] = 0.78
            scores["shareability"] = 0.82
            scores["credibility"] = 0.75
            scores["feedback"].append("Strong hook, needs more specifics")
        
        if "HRValidation" in self.agents:
            scores["safety"] = 1.0
        
        # Overall 계산
        scores["overall"] = (
            scores["clarity"] * 0.2 +
            scores["novelty"] * 0.2 +
            scores["shareability"] * 0.3 +
            scores["credibility"] * 0.2 +
            scores["safety"] * 0.1
        )
        
        return scores
    
    @weave.op()
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
    
    print("🚀 합의 기반 콘텐츠 생성 시스템 테스트")
    print("=" * 70)
    
    # 1. 에이전트 팀 생성
    print("\n1️⃣ HR Agent로 초기 팀 생성...")
    team_state = load_team_state("examples/mason_weavehack2_empty.json")
    result = analyze_team_and_decide(json.dumps(team_state))
    hr_decisions = json.loads(result)
    
    agents = {}
    agents = apply_hr_decisions(agents, hr_decisions, verbose=False)
    
    # 2. 콘텐츠 생성 (합의 기반)
    print(f"\n2️⃣ {len(agents)}명의 에이전트로 콘텐츠 생성...")
    
    generator = ContentGenerator(agents, {
        "max_iterations": 3,  # Demo용 3회
        "min_quality_score": 0.75,
        "min_safety_score": 0.9
    })
    
    content, iterations, scores = generator.generate(
        topic="Building self-optimizing agents for WeaveHack2",
        verbose=True
    )
    
    print(f"\n{'='*70}")
    print("📊 최종 결과")
    print(f"{'='*70}")
    print(f"✅ Iterations: {iterations}")
    print(f"📈 Final Score: {scores['overall']:.2f}")
    print(f"\n📝 Final Content:")
    print(content)

