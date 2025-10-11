"""
CMO Agent 간단한 실행 예제
"""

import json
from cmo_agent.agent import orchestrate_content_creation


def main():
    """CMO 에이전트 실행 예제"""
    
    print("🚀 CMO Agent 실행 예제")
    print("=" * 70 + "\n")
    
    # 설정
    iteration = 0
    topic = "AI agents that hire other AI agents for WeaveHack2"
    num_candidates = 4
    
    print(f"설정:")
    print(f"  - 반복: {iteration}")
    print(f"  - 주제: {topic}")
    print(f"  - 후보 수: {num_candidates}\n")
    
    # CMO 실행
    result_json = orchestrate_content_creation(
        iteration=iteration,
        topic=topic,
        num_candidates=num_candidates
    )
    
    # 결과 파싱
    result = json.loads(result_json)
    
    # 결과 출력
    print("\n" + "=" * 70)
    print("📊 실행 결과")
    print("=" * 70 + "\n")
    
    if "error" in result:
        print(f"❌ 오류: {result['error']}")
        return
    
    # 후보 요약
    print(f"생성된 후보: {len(result['candidates'])}개\n")
    for i, candidate in enumerate(result['candidates'], 1):
        scores = candidate['scores']
        print(f"{i}. {candidate['text'][:60]}...")
        print(f"   점수: {scores['overall']:.2f} "
              f"(clarity={scores['clarity']:.2f}, "
              f"novelty={scores['novelty']:.2f}, "
              f"shareability={scores['shareability']:.2f})")
        print()
    
    # 선택된 콘텐츠
    selected = result['selected']
    print("=" * 70)
    print("✨ 선택된 최종 콘텐츠")
    print("=" * 70 + "\n")
    print(f"📝 텍스트: {selected['text']}")
    print(f"🎨 미디어: {selected['media_prompt']}")
    print(f"📊 예상 점수: {selected['expected_overall']:.2f}")
    print(f"📤 상태: {result['publish_status']}")
    print(f"\n💡 피드백: {result['feedback_summary']}")
    
    # 결과 저장
    output_file = f"cmo_iteration_{iteration}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    main()

