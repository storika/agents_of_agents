"""
에이전트 생성 및 관리 헬퍼
"""

from google.adk.agents.llm_agent import Agent
from typing import Dict, List, Any
import json


def create_agent_from_hire_plan(hire_plan: Dict[str, Any]) -> Agent:
    """
    HR Agent의 hire_plan을 실제 ADK Agent로 변환.
    
    Args:
        hire_plan: HirePlan 딕셔너리
            {
                "name": "ViralHook",
                "role": "writer.specialist",
                "system_prompt": "You are...",
                "reason": "...",
                "config": {"model": "gemini-2.5-flash", ...},
                "tools": []
            }
    
    Returns:
        Agent: 실제 ADK Agent 인스턴스
    """
    config = hire_plan.get("config", {})
    
    agent = Agent(
        model=config.get("model", "gemini-2.5-flash"),
        name=hire_plan["name"],
        description=f"{hire_plan['role']} - {hire_plan['reason']}",
        instruction=hire_plan["system_prompt"],
        # tools는 별도로 추가 필요 (FunctionTool 등)
    )
    
    print(f"✅ Created agent: {hire_plan['name']} ({hire_plan['role']})")
    return agent


def apply_hr_decisions(
    current_agents: Dict[str, Agent],
    hr_decisions: Dict[str, Any],
    verbose: bool = True
) -> Dict[str, Agent]:
    """
    HR 결정을 실제 에이전트 팀에 적용.
    
    Args:
        current_agents: 현재 에이전트 딕셔너리 {name: Agent}
        hr_decisions: HR Agent의 결정
        verbose: 로그 출력 여부
    
    Returns:
        Dict[str, Agent]: 업데이트된 에이전트 딕셔너리
    """
    if verbose:
        print("\n🤖 HR 결정 적용 중...")
        print("=" * 70)
    
    # 1. HIRE - 새로운 에이전트 추가
    for hire in hr_decisions.get("hire_plan", []):
        if verbose:
            print(f"\n[HIRE] {hire['name']} ({hire['role']})")
            print(f"  이유: {hire['reason']}")
        
        current_agents[hire["name"]] = create_agent_from_hire_plan(hire)
    
    # 2. PRUNE - 저성과 에이전트 제거
    for prune in hr_decisions.get("prune_list", []):
        if verbose:
            print(f"\n[PRUNE] {prune['name']}")
            print(f"  이유: {prune['reason']}")
        
        if prune["name"] in current_agents:
            del current_agents[prune["name"]]
    
    # 3. MERGE - 중복 에이전트 병합 (TODO: 실제 병합 로직)
    for merge in hr_decisions.get("merge_plan", []):
        if verbose:
            print(f"\n[MERGE] {merge['a']} + {merge['b']}")
            print(f"  이유: {merge['reason']}")
        
        # 병합 로직은 복잡하므로 현재는 두 에이전트 중 하나만 유지
        if merge["a"] in current_agents and merge["b"] in current_agents:
            # 나중에 생성된 것 (b) 제거
            del current_agents[merge["b"]]
    
    # 4. COACH - 프롬프트 개선 (에이전트 재생성)
    for feedback in hr_decisions.get("prompt_feedback", []):
        if verbose:
            print(f"\n[COACH] {feedback['agent']}")
            print(f"  피드백: {feedback['suggestion'][:80]}...")
        
        if feedback["agent"] in current_agents:
            agent = current_agents[feedback["agent"]]
            
            # 기존 instruction에 코칭 피드백 추가
            updated_instruction = f"""{agent.instruction}

## Coaching Feedback (Applied)
{feedback['suggestion']}"""
            
            # 에이전트 재생성 (instruction 업데이트)
            current_agents[feedback["agent"]] = Agent(
                model=agent.model,
                name=agent.name,
                description=agent.description,
                instruction=updated_instruction,
                tools=agent.tools,
            )
    
    if verbose:
        print(f"\n✅ 현재 팀: {len(current_agents)}명")
        for name in current_agents:
            print(f"  - {name}")
    
    return current_agents


def load_team_state(filepath: str) -> Dict[str, Any]:
    """team_state JSON 로드"""
    with open(filepath) as f:
        return json.load(f)


def save_hr_decisions(decisions: Dict[str, Any], filepath: str):
    """HR 결정 저장"""
    with open(filepath, 'w') as f:
        json.dump(decisions, f, indent=2, ensure_ascii=False)


# 사용 예시
if __name__ == "__main__":
    from hr_validation_agent.agent import analyze_team_and_decide
    
    print("🚀 Mason을 바이럴시키기 위한 초기 팀 생성")
    print("=" * 70)
    
    # 1. 빈 팀으로 시작
    team_state = load_team_state("examples/mason_weavehack2_empty.json")
    
    # 2. HR Agent 실행
    result = analyze_team_and_decide(json.dumps(team_state))
    hr_decisions = json.loads(result)
    
    # 3. 결정 저장
    save_hr_decisions(hr_decisions, "hr_decisions_iteration_0.json")
    
    # 4. 에이전트 생성
    agents = {}
    agents = apply_hr_decisions(agents, hr_decisions)
    
    print(f"\n✨ 생성 완료! {len(agents)}명의 에이전트가 준비되었습니다.")
    print("\n다음 단계:")
    print("1. agents 딕셔너리를 사용하여 콘텐츠 생성")
    print("2. Twitter에 발행")
    print("3. 메트릭 수집")
    print("4. team_state 업데이트")
    print("5. 다음 iteration 실행")

