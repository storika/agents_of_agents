"""
CMO Agent와 HR Agent 통합 예제
HR Agent의 hire_plan을 받아 서브 에이전트 팀을 구성하고 콘텐츠 생성
"""

import json
from cmo_agent.agent import initialize_sub_agents, orchestrate_content_creation


# HR Agent가 생성한 hire_plan
HR_HIRE_PLAN = [
    {
        "slot": "orchestrator/main",
        "ref": "ContentTeamLead",
        "patch": {},
        "reason": "Initial team setup to fulfill core orchestrator role and guide content strategy."
    },
    {
        "slot": "writer/main",
        "ref": "ViralCopywriter",
        "patch": {},
        "reason": "Initial team setup to fulfill core writer role and create high-engagement copy."
    },
    {
        "slot": "media/main",
        "ref": "MemeCreator",
        "patch": {},
        "reason": "Initial team setup to fulfill core media specialist role with visual content creation."
    },
    {
        "slot": "safety/main",
        "ref": "BrandSafetyValidator",
        "patch": {},
        "reason": "Initial team setup to fulfill core safety agent role and ensure brand alignment."
    },
    {
        "slot": "critic/main",
        "ref": "FactChecker",
        "patch": {},
        "reason": "Initial team setup to fulfill core critic role by verifying factual claims for credibility."
    },
    {
        "slot": "intelligence/performance",
        "ref": "PerformanceAnalyst",
        "patch": {},
        "reason": "Adding an intelligence agent to monitor metrics and provide optimization insights for engagement."
    },
    {
        "slot": "intelligence/audience",
        "ref": "AudienceResearcher",
        "patch": {},
        "reason": "Adding an intelligence agent to analyze audience data and recommend content angles for engagement."
    }
]


def main():
    """HR-CMO 통합 워크플로우"""
    
    print("🚀 CMO Agent + HR Agent 통합 예제")
    print("=" * 70 + "\n")
    
    # === STEP 1: HR Agent의 hire_plan으로 서브 에이전트 팀 초기화 ===
    print("STEP 1: 서브 에이전트 팀 초기화\n")
    
    init_result = initialize_sub_agents(HR_HIRE_PLAN)
    init_data = json.loads(init_result)
    
    if init_data["status"] == "success":
        print(f"✅ {init_data['message']}")
        print(f"\n활성 에이전트:")
        for slot, name in init_data["agents"].items():
            print(f"  - {slot}: {name}")
    else:
        print(f"❌ 초기화 실패: {init_data['message']}")
        return
    
    # === STEP 2: CMO로 콘텐츠 생성 (서브 에이전트 활용) ===
    print("\n" + "=" * 70)
    print("STEP 2: 콘텐츠 생성 시작")
    print("=" * 70 + "\n")
    
    topic = "AI agents that hire other AI agents - WeaveHack2 프로젝트"
    
    # 모드 선택
    print("모드 선택:")
    print("  1. 시뮬레이션 모드 (빠름, 테스트용)")
    print("  2. 서브 에이전트 모드 (실제 에이전트 호출)\n")
    
    # 여기서는 시뮬레이션 모드로 실행 (실제 에이전트는 API 키 필요)
    use_sub_agents = False
    mode_name = "시뮬레이션" if not use_sub_agents else "서브 에이전트"
    print(f"선택: {mode_name} 모드\n")
    
    result_json = orchestrate_content_creation(
        iteration=0,
        topic=topic,
        num_candidates=5,
        use_sub_agents=use_sub_agents
    )
    
    result = json.loads(result_json)
    
    # === STEP 3: 결과 출력 ===
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
        print(f"{i}. {candidate['text']}")
        print(f"   점수: {scores['overall']:.2f} "
              f"(clarity={scores['clarity']:.2f}, "
              f"novelty={scores['novelty']:.2f}, "
              f"shareability={scores['shareability']:.2f}, "
              f"safety={scores['safety']:.2f})")
        print()
    
    # 선택된 콘텐츠
    selected = result['selected']
    print("=" * 70)
    print("✨ 선택된 최종 콘텐츠")
    print("=" * 70 + "\n")
    print(f"📝 텍스트: {selected['text']}")
    print(f"🎨 미디어: {selected['media_prompt']}")
    print(f"📷 모드: {selected['mode']}")
    print(f"📊 예상 점수: {selected['expected_overall']:.2f}")
    print(f"📤 상태: {result['publish_status']}")
    print(f"\n💡 피드백: {result['feedback_summary']}")
    
    # === STEP 4: 결과 저장 ===
    output_file = "cmo_hr_integrated_iteration_0.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 결과가 {output_file}에 저장되었습니다.")
    
    # === STEP 5: 서브 에이전트 팀 상태 ===
    print("\n" + "=" * 70)
    print("🤖 서브 에이전트 팀 상태")
    print("=" * 70 + "\n")
    
    print(f"총 {init_data['team_size']}명의 에이전트가 활성화되어 있습니다:")
    
    categories = {
        "orchestrator": "오케스트레이터",
        "writer": "작가",
        "media": "미디어 전문가",
        "safety": "안전성 검증",
        "critic": "비평가",
        "intelligence": "인텔리전스"
    }
    
    for category, category_name in categories.items():
        agents = [name for slot, name in init_data["agents"].items() if slot.startswith(category)]
        if agents:
            print(f"  {category_name}: {', '.join(agents)}")
    
    print("\n✅ 모든 프로세스 완료!")


if __name__ == "__main__":
    main()

