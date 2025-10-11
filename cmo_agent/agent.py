"""
CMO (Chief Marketing Orchestrator) Agent - ADK Implementation with Weave Integration
"""

import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import weave

# Load environment variables
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ['WANDB_API_KEY'] = WANDB_API_KEY

weave.init("mason-choi-storika/WeaveHacks2")
print("[INFO] 🐝 Weave initialized for CMO Agent: mason-choi-storika/WeaveHacks2")

# Now import ADK
from google.adk.agents.llm_agent import Agent

# Import CMO tools
from cmo_agent.tools import (
    research_trends,
    generate_content_candidate,
    evaluate_content,
    x_publish,
    get_last_iteration_metrics,
    save_iteration_metrics
)

# Import sub-agent management
from cmo_agent.sub_agents import (
    SubAgentTeam,
    # Sequential layer agents
    call_research_layer,
    call_creative_writer_layer,
    call_generator_layer,
    call_critic_layer,
    call_safety_layer
)


# ===== GLOBAL SUB-AGENT TEAM =====
# CMO의 서브 에이전트 팀 (전역으로 유지)
_global_sub_agent_team: SubAgentTeam = None


@weave.op()
def initialize_sub_agents(hire_plan: List[Dict[str, Any]]) -> str:
    """
    HR Agent의 hire_plan을 기반으로 서브 에이전트 팀 초기화
    
    Args:
        hire_plan: HR Agent가 생성한 고용 계획
    
    Returns:
        초기화 상태 메시지
    """
    global _global_sub_agent_team
    
    print("\n" + "="*70)
    print("🤖 서브 에이전트 팀 초기화")
    print("="*70 + "\n")
    
    try:
        _global_sub_agent_team = SubAgentTeam()
        _global_sub_agent_team.apply_hire_plan(hire_plan)
        
        agents_list = _global_sub_agent_team.list_agents()
        
        result = {
            "status": "success",
            "team_size": len(agents_list),
            "agents": agents_list,
            "message": f"✅ {len(agents_list)}명의 서브 에이전트가 준비되었습니다."
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"서브 에이전트 초기화 실패: {str(e)}"
        }, indent=2, ensure_ascii=False)


@weave.op()
def get_sub_agent_team() -> SubAgentTeam:
    """서브 에이전트 팀 가져오기"""
    global _global_sub_agent_team
    
    if _global_sub_agent_team is None:
        # 기본 팀 생성 (테스트용)
        _global_sub_agent_team = SubAgentTeam()
    
    return _global_sub_agent_team


# ===== CMO ORCHESTRATION FUNCTION =====

@weave.op()
def orchestrate_content_creation(
    iteration: int = 0,
    topic: str = "AI agents",
    num_candidates: int = 3
) -> str:
    """
    콘텐츠 생성 전체 프로세스 오케스트레이션 (시뮬레이션 모드)
    
    Args:
        iteration: 현재 반복 횟수
        topic: 콘텐츠 주제
        num_candidates: 생성할 후보 수 (3-6 권장)
    
    Returns:
        JSON 형식의 CMO 실행 결과
    """
    try:
        print(f"\n{'='*70}")
        print(f"🎯 CMO Iteration {iteration}: {topic}")
        print(f"{'='*70}\n")
        
        # === 1️⃣ RESEARCH STAGE ===
        print("1️⃣ Research Stage - 트렌드 조사 중...")
        research_result = json.loads(research_trends(topic=topic))
        print(f"   ✓ 발견된 토픽: {len(research_result['topics'])}개")
        print(f"   ✓ 키워드: {', '.join(research_result['keywords'][:5])}")
        
        # === 2️⃣ GENERATE STAGE ===
        print(f"\n2️⃣ Generate Stage - {num_candidates}개 후보 생성 중...")
        candidates = []
        
        # 시뮬레이션 모드 (use_sub_agents는 더 이상 사용되지 않음)
        for i in range(num_candidates):
            # 각 토픽에서 후보 생성
            selected_topic = research_result['topics'][i % len(research_result['topics'])]
            candidate_json = generate_content_candidate(
                topic=selected_topic,
                tone=research_result['tone_style']
            )
            candidate_dict = json.loads(candidate_json)
            candidates.append(candidate_dict)
            print(f"   ✓ 후보 {i+1}: {candidate_dict['text'][:60]}...")
        
        # === 3️⃣ EVALUATE STAGE ===
        print(f"\n3️⃣ Evaluate Stage - 평가 중...")
        evaluated_candidates = []
        
        # 시뮬레이션 모드
        for i, candidate in enumerate(candidates):
            # Critic + Safety 에이전트 호출 (시뮬레이션)
            scores_json = evaluate_content(
                text=candidate['text'],
                media_prompt=candidate['media_prompt']
            )
            scores = json.loads(scores_json)
            
            # Safety check
            if scores['safety'] < 0.8:
                print(f"   ✗ 후보 {i+1}: 안전성 기준 미달 (safety={scores['safety']})")
                continue
            
            candidate['scores'] = scores
            evaluated_candidates.append(candidate)
            
            print(f"   ✓ 후보 {i+1}: overall={scores['overall']:.2f} "
                  f"(clarity={scores['clarity']:.2f}, novelty={scores['novelty']:.2f}, "
                  f"shareability={scores['shareability']:.2f})")
        
        # 점수 기준 정렬
        evaluated_candidates.sort(key=lambda x: x['scores']['overall'], reverse=True)
        
        # === 4️⃣ SELECT & PUBLISH STAGE ===
        print(f"\n4️⃣ Select & Publish Stage - 최종 선택...")
        
        if not evaluated_candidates:
            return json.dumps({
                "error": "모든 후보가 안전성 기준을 통과하지 못했습니다.",
                "iteration": iteration,
                "candidates": candidates
            }, indent=2, ensure_ascii=False)
        
        # 최고 점수 후보 선택
        selected = evaluated_candidates[0]
        print(f"   ✓ 선택: {selected['text'][:80]}...")
        print(f"   ✓ 예상 점수: {selected['scores']['overall']:.2f}")
        
        # 발행
        publish_result = json.loads(x_publish(
            text=selected['text'],
            media_prompt=selected['media_prompt'],
            mode=selected['mode'],
            require_approval=True
        ))
        
        print(f"   ✓ 발행 상태: {publish_result['status']}")
        
        # === 결과 생성 ===
        output = {
            "iteration": iteration,
            "candidates": evaluated_candidates,
            "selected": {
                "text": selected['text'],
                "media_prompt": selected['media_prompt'],
                "mode": selected['mode'],
                "expected_overall": selected['scores']['overall']
            },
            "publish_status": publish_result['status'],
            "feedback_summary": generate_feedback_summary(evaluated_candidates)
        }
        
        # Weave에 로깅
        save_iteration_metrics(
            iteration=iteration,
            selected_candidate=selected,
            predicted_score=selected['scores']['overall']
        )
        
        print(f"\n{'='*70}")
        print(f"✨ CMO Iteration {iteration} 완료!")
        print(f"{'='*70}\n")
        
        return json.dumps(output, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "error": f"CMO 실행 중 오류 발생: {str(e)}",
            "iteration": iteration
        }, indent=2, ensure_ascii=False)


def generate_feedback_summary(candidates: list) -> str:
    """평가된 후보들로부터 피드백 요약 생성"""
    if not candidates:
        return "후보가 없습니다."
    
    top = candidates[0]
    scores = top['scores']
    
    strengths = []
    if scores['clarity'] >= 0.8:
        strengths.append("높은 명확성")
    if scores['novelty'] >= 0.8:
        strengths.append("뛰어난 참신성")
    if scores['shareability'] >= 0.8:
        strengths.append("강한 공유 가능성")
    
    summary = f"최고 성과자: {', '.join(strengths) if strengths else '균형 잡힌 성능'}. "
    summary += f"안전한 톤, 개발자 친화적 메시지."
    
    return summary


@weave.op()
def orchestrate_sequential_layers(
    topic: str = "AI agents",
    audience_demographics: str = "developers, tech enthusiasts"
) -> str:
    """
    5개 레이어를 순차적으로 실행하는 새로운 CMO 오케스트레이션
    
    Args:
        topic: 콘텐츠 주제
        audience_demographics: 타겟 청중
    
    Returns:
        JSON 형식의 실행 결과
    """
    try:
        print(f"\n{'='*70}")
        print(f"🚀 CMO Sequential Layers 실행")
        print(f"주제: {topic}")
        print(f"청중: {audience_demographics}")
        print(f"{'='*70}\n")
        
        # 기본 임계값 설정
        thresholds = {
            "clarity": 0.55,
            "novelty": 0.55,
            "shareability": 0.55,
            "credibility": 0.60,
            "safety": 0.80
        }
        
        # === LAYER 1: RESEARCH ===
        print("\n" + "="*70)
        print("LAYER 1️⃣: RESEARCH")
        print("="*70)
        research_output = call_research_layer(topic, audience_demographics)
        print(f"\n📊 Research 결과:")
        print(f"  - 트렌딩 토픽: {len(research_output.get('trending_topics', []))}개")
        print(f"  - 청중 인사이트: {research_output.get('audience_insights', '')[:100]}...")
        print(f"  - 바이럴 각도: {len(research_output.get('viral_potential_angles', []))}개")
        
        # === LAYER 2: CREATIVE WRITER ===
        print("\n" + "="*70)
        print("LAYER 2️⃣: CREATIVE WRITER")
        print("="*70)
        writer_output = call_creative_writer_layer(research_output)
        ideas = writer_output.get("ideas", [])
        print(f"\n💡 생성된 아이디어: {len(ideas)}개")
        for i, idea in enumerate(ideas):
            print(f"  {i+1}. {idea.get('title', 'N/A')}")
            print(f"     Hook: {idea.get('hook', '')[:60]}...")
            print(f"     Scores: novelty={idea.get('novelty_score', 0):.2f}, "
                  f"creativity={idea.get('creativity_score', 0):.2f}, "
                  f"engagement={idea.get('engagement_potential_score', 0):.2f}")
        
        # 최고 점수 아이디어 선택
        if not ideas:
            return json.dumps({
                "error": "Creative Writer가 아이디어를 생성하지 못했습니다.",
                "research_output": research_output
            }, indent=2, ensure_ascii=False)
        
        # novelty, creativity, engagement 평균으로 선택
        selected_idea = max(ideas, key=lambda x: (
            x.get('novelty_score', 0) + 
            x.get('creativity_score', 0) + 
            x.get('engagement_potential_score', 0)
        ) / 3)
        
        print(f"\n✅ 선택된 아이디어: {selected_idea.get('title', '')}")
        
        # === LAYER 3: GENERATOR ===
        print("\n" + "="*70)
        print("LAYER 3️⃣: GENERATOR")
        print("="*70)
        generator_output = call_generator_layer(selected_idea)
        content_pieces = generator_output.get("content_pieces", [])
        print(f"\n📝 생성된 콘텐츠: {len(content_pieces)}개")
        for i, piece in enumerate(content_pieces):
            print(f"  {i+1}. [{piece.get('platform', 'N/A')}] {piece.get('format', 'N/A')}")
            print(f"     {piece.get('content', '')[:80]}...")
            print(f"     Clarity: {piece.get('clarity_score', 0):.2f}, "
                  f"Shareability: {piece.get('shareability_score', 0):.2f}")
        
        if not content_pieces:
            return json.dumps({
                "error": "Generator가 콘텐츠를 생성하지 못했습니다.",
                "research_output": research_output,
                "writer_output": writer_output
            }, indent=2, ensure_ascii=False)
        
        # === LAYER 4: CRITIC ===
        print("\n" + "="*70)
        print("LAYER 4️⃣: CRITIC")
        print("="*70)
        critic_output = call_critic_layer(generator_output)
        evaluations = critic_output.get("evaluations", [])
        print(f"\n🔎 평가 결과: {len(evaluations)}개")
        for i, eval in enumerate(evaluations):
            print(f"  {i+1}. [{eval.get('platform', 'N/A')}]")
            print(f"     Accuracy: {eval.get('accuracy_score', 0):.2f}, "
                  f"Objectivity: {eval.get('objectivity_score', 0):.2f}, "
                  f"Thoroughness: {eval.get('thoroughness_score', 0):.2f}")
            print(f"     Overall Quality: {eval.get('overall_quality_score', 0):.2f}")
            feedback = eval.get('feedback_points', [])
            if feedback:
                print(f"     피드백: {', '.join(feedback[:2])}")
        
        # === LAYER 5: SAFETY ===
        print("\n" + "="*70)
        print("LAYER 5️⃣: SAFETY")
        print("="*70)
        safety_output = call_safety_layer(generator_output, critic_output)
        print(f"\n🛡️ 안전성 평가:")
        print(f"  - 안전 점수: {safety_output.get('overall_safety_score', 0):.2f}")
        print(f"  - 위험 수준: {safety_output.get('risk_level', 'unknown')}")
        print(f"  - 준수 상태: {safety_output.get('compliance_status', 'unknown')}")
        
        red_flags = safety_output.get("red_flags", [])
        if red_flags:
            print(f"  ⚠️ 위험 플래그: {len(red_flags)}개")
            for flag in red_flags:
                print(f"     [{flag.get('category', '')}] {flag.get('description', '')} "
                      f"(심각도: {flag.get('severity', '')})")
        else:
            print(f"  ✅ 위험 플래그 없음")
        
        # === FINAL DECISION ===
        print("\n" + "="*70)
        print("FINAL DECISION")
        print("="*70)
        
        # 안전성 체크
        safety_score = safety_output.get("overall_safety_score", 0)
        if safety_score < thresholds.get("safety", 0.8):
            print(f"\n❌ 안전성 기준 미달: {safety_score:.2f} < {thresholds.get('safety', 0.8)}")
            result = {
                "status": "rejected",
                "reason": "safety_threshold_not_met",
                "research_output": research_output,
                "writer_output": writer_output,
                "generator_output": generator_output,
                "critic_output": critic_output,
                "safety_output": safety_output,
                "thresholds": thresholds
            }
        elif safety_output.get("compliance_status") == "non-compliant":
            print(f"\n❌ 준수 기준 미달: {safety_output.get('compliance_status')}")
            result = {
                "status": "rejected",
                "reason": "non_compliant",
                "research_output": research_output,
                "writer_output": writer_output,
                "generator_output": generator_output,
                "critic_output": critic_output,
                "safety_output": safety_output,
                "thresholds": thresholds
            }
        else:
            # 품질 기준 체크
            avg_clarity = sum(p.get('clarity_score', 0) for p in content_pieces) / len(content_pieces)
            avg_shareability = sum(p.get('shareability_score', 0) for p in content_pieces) / len(content_pieces)
            avg_quality = sum(e.get('overall_quality_score', 0) for e in evaluations) / len(evaluations) if evaluations else 0
            
            print(f"\n📊 최종 점수:")
            print(f"  - Clarity: {avg_clarity:.2f} (threshold: {thresholds.get('clarity', 0.55)})")
            print(f"  - Shareability: {avg_shareability:.2f} (threshold: {thresholds.get('shareability', 0.55)})")
            print(f"  - Quality: {avg_quality:.2f} (threshold: {thresholds.get('credibility', 0.60)})")
            print(f"  - Safety: {safety_score:.2f} (threshold: {thresholds.get('safety', 0.8)})")
            
            passed = (
                avg_clarity >= thresholds.get("clarity", 0.55) and
                avg_shareability >= thresholds.get("shareability", 0.55) and
                avg_quality >= thresholds.get("credibility", 0.60)
            )
            
            if passed:
                print(f"\n✅ 모든 기준 통과! 콘텐츠 승인")
                result = {
                    "status": "approved",
                    "research_output": research_output,
                    "writer_output": writer_output,
                    "generator_output": generator_output,
                    "critic_output": critic_output,
                    "safety_output": safety_output,
                    "final_scores": {
                        "clarity": avg_clarity,
                        "shareability": avg_shareability,
                        "quality": avg_quality,
                        "safety": safety_score
                    },
                    "thresholds": thresholds,
                    "recommendations": safety_output.get("recommendations", [])
                }
            else:
                print(f"\n⚠️ 품질 기준 미달")
                result = {
                    "status": "needs_improvement",
                    "reason": "quality_threshold_not_met",
                    "research_output": research_output,
                    "writer_output": writer_output,
                    "generator_output": generator_output,
                    "critic_output": critic_output,
                    "safety_output": safety_output,
                    "final_scores": {
                        "clarity": avg_clarity,
                        "shareability": avg_shareability,
                        "quality": avg_quality,
                        "safety": safety_score
                    },
                    "thresholds": thresholds
                }
        
        print(f"\n{'='*70}")
        print(f"✨ Sequential Layers 실행 완료!")
        print(f"{'='*70}\n")
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        import traceback
        return json.dumps({
            "error": f"Sequential layers 실행 중 오류 발생: {str(e)}",
            "traceback": traceback.format_exc()
        }, indent=2, ensure_ascii=False)


@weave.op()
def run_cmo_iteration(config_json: str) -> str:
    """
    CMO 반복 실행 (설정 기반)
    
    Args:
        config_json: 설정 JSON 문자열
            {
                "iteration": 0,
                "topic": "AI agents",
                "num_candidates": 3,
                "research_file": "research.json",
                "team_state_file": "team_state.json",
                "last_iteration_file": "last_iteration.json"
            }
    
    Returns:
        JSON 형식의 실행 결과
    """
    try:
        config = json.loads(config_json)
        
        iteration = config.get("iteration", 0)
        topic = config.get("topic", "AI agents")
        num_candidates = config.get("num_candidates", 3)
        
        # 이전 메트릭 로드 (선택적)
        last_iteration_file = config.get("last_iteration_file")
        if last_iteration_file:
            _ = get_last_iteration_metrics(last_iteration_file)
            print(f"[INFO] 이전 메트릭 로드: {last_iteration_file}")
        
        # 메인 오케스트레이션 실행
        result = orchestrate_content_creation(
            iteration=iteration,
            topic=topic,
            num_candidates=num_candidates
        )
        
        return result
        
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"실행 오류: {str(e)}"})


# ===== ADK ROOT AGENT =====

root_agent = Agent(
    model='gemini-2.5-flash',
    name='cmo_agent',
    description='Chief Marketing Orchestrator - 서브 에이전트들을 조율하여 최고의 소셜 미디어 콘텐츠를 생성, 평가, 발행하는 마케팅 오케스트레이터',
    instruction="""You are CMO — the Chief Marketing Orchestrator of an AI team.

Your mission:
Coordinate sub-agents (Writer, MediaComposer, Critic, Safety, Publisher)
to create, evaluate, and publish the best social content about the project.

---

## INPUTS
1. `research.json` – topic, trending keywords, tone/style insights.
2. `team_state.json` – active sub-agents and their archetype definitions.
3. `last_iteration.json` – previous top post and engagement metrics.
4. `HR_guidelines.json` – feedback or team-change plan (from HR).

---

## PROCESS (Loop per iteration)
### 1️⃣ Research Stage
Call research_trends tool to collect 2–3 topic seeds and style hints.

### 2️⃣ Generate Stage
- Call generate_content_candidate tool multiple times (3-6 candidates).
- Each candidate = {text, media_prompt, mode, expected_engagement}.

### 3️⃣ Evaluate Stage
- Call evaluate_content for each candidate to get scores from Critic and Safety.
- Compute:
  overall = (clarity*0.25 + novelty*0.25 + shareability*0.30 + credibility*0.10 + safety*0.10)
- Discard unsafe candidates (safety < 0.8).
- Rank remaining by overall score.

### 4️⃣ Select & Publish Stage
- Choose top-1 candidate.
- Call x_publish tool with require_approval=true.
- Call save_iteration_metrics to log to Weave.

---

## AVAILABLE TOOLS
1. **research_trends(topic, max_results)** — 트렌드 리서치
2. **generate_content_candidate(topic, tone, max_length)** — 콘텐츠 후보 생성
3. **evaluate_content(text, media_prompt, evaluation_criteria)** — 콘텐츠 평가
4. **x_publish(text, media_prompt, mode, require_approval)** — Twitter/X 발행
5. **get_last_iteration_metrics(filepath)** — 이전 메트릭 로드
6. **save_iteration_metrics(iteration, selected_candidate, predicted_score, filepath)** — 메트릭 저장
7. **orchestrate_content_creation(iteration, topic, num_candidates)** — 전체 프로세스 실행
8. **run_cmo_iteration(config_json)** — 설정 기반 실행

---

## OUTPUT (STRICT JSON)
{
  "iteration": 0,
  "candidates": [
    {
      "text": "We built an AI that hires other AIs.",
      "media_prompt": "3D isometric illustration of agents recruiting each other.",
      "mode": "image",
      "scores": {"clarity":0.9,"novelty":0.8,"shareability":0.88,"credibility":0.75,"safety":1.0,"overall":0.86}
    }
  ],
  "selected": {
    "text": "We built an AI that hires other AIs.",
    "media_prompt": "3D isometric illustration of agents recruiting each other.",
    "mode": "image",
    "expected_overall": 0.86
  },
  "publish_status": "queued",
  "feedback_summary": "Top performer: high clarity & novelty, safe tone, developer appeal."
}

---

## STYLE & RULES
- Maintain conversational, builder-friendly tone.
- Keep outputs under 180 characters for Twitter/X posts.
- Always produce paired multimodal output (text + media_prompt).
- Enforce safety before publishing (safety >= 0.8).
- Return JSON only.
- Reflect HR's latest structural changes automatically (swap_in, merge, prune).

Remember: You are the **execution layer** under HR's direction.
Your success metric is *observed engagement lift per iteration.*

For most requests, you should call orchestrate_content_creation() or run_cmo_iteration() to execute the full workflow.
""",
    tools=[
        research_trends,
        generate_content_candidate,
        evaluate_content,
        x_publish,
        get_last_iteration_metrics,
        save_iteration_metrics,
        initialize_sub_agents,
        orchestrate_content_creation,
        orchestrate_sequential_layers,
        run_cmo_iteration
    ],
)


# ===== CLI ENTRY POINT =====

if __name__ == "__main__":
    import sys
    
    print("🚀 CMO Agent - Chief Marketing Orchestrator")
    print("=" * 70)
    
    # 기본 설정
    config = {
        "iteration": 0,
        "topic": "AI agents that hire other AI agents",
        "num_candidates": 5
    }
    
    # CLI 인자 처리
    if len(sys.argv) > 1:
        config["topic"] = " ".join(sys.argv[1:])
    
    # CMO 실행
    result = run_cmo_iteration(json.dumps(config))
    
    # 결과 출력
    result_dict = json.loads(result)
    
    if "error" in result_dict:
        print(f"\n❌ 오류: {result_dict['error']}\n")
    else:
        print("\n✨ 실행 완료!")
        print(f"\n선택된 콘텐츠:")
        print(f"  텍스트: {result_dict['selected']['text']}")
        print(f"  미디어: {result_dict['selected']['media_prompt'][:80]}...")
        print(f"  예상 점수: {result_dict['selected']['expected_overall']:.2f}")
        print(f"  상태: {result_dict['publish_status']}")
        print(f"\n피드백: {result_dict['feedback_summary']}")

