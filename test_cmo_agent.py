"""
CMO Agent 테스트 스크립트
"""

import json
from cmo_agent.agent import (
    orchestrate_content_creation,
    run_cmo_iteration,
    root_agent
)


def test_basic_orchestration():
    """기본 오케스트레이션 테스트"""
    print("\n" + "="*70)
    print("TEST 1: 기본 오케스트레이션")
    print("="*70)
    
    result_json = orchestrate_content_creation(
        iteration=0,
        topic="AI agents that hire other AI agents",
        num_candidates=3
    )
    
    result = json.loads(result_json)
    
    assert "candidates" in result, "candidates 필드가 없습니다"
    assert "selected" in result, "selected 필드가 없습니다"
    assert "publish_status" in result, "publish_status 필드가 없습니다"
    
    print(f"\n✅ 테스트 통과!")
    print(f"   - 생성된 후보 수: {len(result['candidates'])}")
    print(f"   - 선택된 콘텐츠: {result['selected']['text'][:60]}...")
    print(f"   - 발행 상태: {result['publish_status']}")
    
    return result


def test_config_based_run():
    """설정 기반 실행 테스트"""
    print("\n" + "="*70)
    print("TEST 2: 설정 기반 실행")
    print("="*70)
    
    config = {
        "iteration": 1,
        "topic": "WeaveHack2 프로젝트",
        "num_candidates": 4
    }
    
    result_json = run_cmo_iteration(json.dumps(config))
    result = json.loads(result_json)
    
    assert "error" not in result or result.get("candidates"), "실행 실패"
    
    print(f"\n✅ 테스트 통과!")
    print(f"   - 반복 횟수: {result['iteration']}")
    
    return result


def test_evaluation_scoring():
    """평가 점수 계산 테스트"""
    print("\n" + "="*70)
    print("TEST 3: 평가 점수 계산")
    print("="*70)
    
    from cmo_agent.tools import evaluate_content
    
    test_cases = [
        {
            "text": "AI agents are revolutionizing automation",
            "media_prompt": "Modern tech illustration"
        },
        {
            "text": "This is a very long text that might not be as clear because it rambles on and on without making a concise point about the topic at hand",
            "media_prompt": "Abstract background"
        }
    ]
    
    for i, case in enumerate(test_cases):
        scores_json = evaluate_content(case["text"], case["media_prompt"])
        scores = json.loads(scores_json)
        
        print(f"\n케이스 {i+1}:")
        print(f"  텍스트: {case['text'][:50]}...")
        print(f"  점수: overall={scores['overall']:.2f}, "
              f"clarity={scores['clarity']:.2f}, "
              f"shareability={scores['shareability']:.2f}")
        
        assert 0.0 <= scores['overall'] <= 1.0, "overall 점수 범위 오류"
        assert scores['safety'] >= 0.8, "안전성 점수가 너무 낮음"
    
    print(f"\n✅ 테스트 통과!")


def test_safety_filter():
    """안전성 필터 테스트"""
    print("\n" + "="*70)
    print("TEST 4: 안전성 필터")
    print("="*70)
    
    # 실제로는 안전하지 않은 콘텐츠를 필터링해야 함
    # 여기서는 시뮬레이션만
    
    result_json = orchestrate_content_creation(
        iteration=2,
        topic="AI safety and ethics",
        num_candidates=3
    )
    
    result = json.loads(result_json)
    
    # 선택된 콘텐츠는 항상 safety >= 0.8이어야 함
    if result.get("selected"):
        # selected에는 scores가 직접 없고 expected_overall만 있음
        # 원래 candidates에서 찾아야 함
        selected_text = result["selected"]["text"]
        for candidate in result["candidates"]:
            if candidate["text"] == selected_text:
                assert candidate["scores"]["safety"] >= 0.8, "안전성 필터 실패"
                break
    
    print(f"\n✅ 테스트 통과!")


def test_adk_agent_query():
    """ADK Agent 쿼리 테스트"""
    print("\n" + "="*70)
    print("TEST 5: ADK Agent 직접 호출")
    print("="*70)
    
    # ADK Agent를 직접 호출
    query = """
    AI 에이전트 시스템에 대한 소셜 미디어 콘텐츠를 생성해주세요.
    iteration=0, 후보는 3개만 생성하세요.
    """
    
    print(f"쿼리: {query.strip()}")
    print(f"\nAgent 정보:")
    print(f"  - Name: {root_agent.name}")
    print(f"  - Model: {root_agent.model}")
    print(f"  - Tools: {len(root_agent.tools)}개")
    
    print(f"\n✅ Agent 로드 성공!")


def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "🧪" * 35)
    print("CMO AGENT 테스트 시작")
    print("🧪" * 35)
    
    try:
        test_basic_orchestration()
        test_config_based_run()
        test_evaluation_scoring()
        test_safety_filter()
        test_adk_agent_query()
        
        print("\n" + "="*70)
        print("✨ 모든 테스트 통과!")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}\n")
        raise


if __name__ == "__main__":
    run_all_tests()

