"""
HR Validation Agent를 실행하고 자동으로 CMO Agent 새 버전 생성
ADK Agent tool을 사용하여 완전 자동화된 워크플로우
"""

import asyncio
import json
from google.adk.runners import InMemoryRunner
from google.genai import types
from hr_validation_agent.agent import root_agent  # Sequential orchestrator by default


async def run_hr_with_auto_versioning(
    input_json_path: str = "hr_input_with_actual_performance.json",
    version_name: str = None
):
    """
    HR Agent를 실행하고 자동으로 CMO Agent를 업데이트
    
    Args:
        input_json_path: HR Agent 입력 JSON 파일 경로
        version_name: 버전 이름 (None이면 자동 생성)
    """
    
    print("=" * 70)
    print("🤖 HR Validation Agent + Auto Versioning 실행")
    print("=" * 70)
    
    # 입력 JSON 로드
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            hr_input = json.load(f)
        print(f"✅ 입력 데이터 로드: {input_json_path}")
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없음: {input_json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return None
    
    # ADK Runner 설정
    runner = InMemoryRunner(agent=root_agent, app_name="hr_validation_agent")
    session_service = runner.session_service
    
    user_id = "hr_manager_01"
    session_id = f"session_auto_{asyncio.get_event_loop().time()}"
    
    await session_service.create_session(
        app_name="hr_validation_agent",
        user_id=user_id,
        session_id=session_id,
    )
    
    print(f"\n📊 세션 생성: {session_id}")
    print(f"📈 Iteration: {hr_input.get('iteration', 0)}")
    print(f"📝 레이어 수: {len(hr_input.get('layers', []))}")
    
    # HR Agent에게 메시지 전송
    user_message = json.dumps(hr_input, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("🔍 HR Agent 실행 중...")
    print("=" * 70)
    
    hr_response = None
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        ),
    ):
        # 중간 이벤트 로깅 (tool calls 등)
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    print(f"\n🔧 Tool 호출: {part.function_call.name}")
                
                if hasattr(part, 'function_response') and part.function_response:
                    print(f"✅ Tool 응답 완료")
        
        # 최종 응답 수집
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    hr_response = part.text.strip()
                    break
    
    if not hr_response:
        print("\n❌ HR Agent 응답을 받지 못했습니다")
        return None
    
    print("\n" + "=" * 70)
    print("✅ HR Agent 응답 완료")
    print("=" * 70)
    
    # 응답 파싱
    try:
        # JSON만 추출 (마크다운 코드 블록 제거)
        if "```json" in hr_response:
            hr_response = hr_response.split("```json")[1].split("```")[0].strip()
        elif "```" in hr_response:
            hr_response = hr_response.split("```")[1].split("```")[0].strip()
        
        hr_decisions = json.loads(hr_response)
        
        print(f"\n📋 HR 결정 사항:")
        print(f"   - 업데이트할 레이어: {len(hr_decisions.get('prompts', []))}개")
        for prompt in hr_decisions.get('prompts', []):
            print(f"     • {prompt['layer']}: {prompt['reason']}")
        
        # 결과 저장
        output_path = f"hr_decisions_iteration_{hr_input.get('iteration', 0)}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(hr_decisions, f, ensure_ascii=False, indent=2)
        print(f"\n💾 HR 결정 저장: {output_path}")
        
    except json.JSONDecodeError as e:
        print(f"\n⚠️ HR 응답 JSON 파싱 실패: {e}")
        print(f"응답 원문:\n{hr_response[:500]}...")
        hr_decisions = None
    
    if not hr_decisions:
        return None
    
    # 자동으로 CMO Agent 업데이트
    print("\n" + "=" * 70)
    print("🚀 CMO Agent 자동 업데이트")
    print("=" * 70)
    
    from cmo_agent.tools_version import apply_prompt_improvements
    
    try:
        # CMO Agent 직접 업데이트
        result_json = apply_prompt_improvements(
            hr_decisions_json=json.dumps(hr_decisions),
            version_name=version_name,
            backup_current=True
        )
        
        result = json.loads(result_json)
        
        if result.get("status") == "success":
            print(f"\n✅ CMO Agent 업데이트 완료!")
            print(f"   버전: {result['version_name']}")
            backup_dir = result.get('backup_path', '').split('/')[-1] if result.get('backup_path') else 'N/A'
            print(f"   이전 버전 백업: {backup_dir}")
            print(f"   업데이트된 레이어: {', '.join(result['updated_layers'])}")
            
            if result.get("applied_to_main"):
                print(f"\n🎯 cmo_agent/sub_agents.py가 직접 업데이트되었습니다!")
                print(f"   ADK가 새로운 프롬프트를 즉시 사용합니다.")
                print(f"\n📦 버전 구조:")
                print(f"   - cmo_agent/ ← 현재 활성 (업데이트됨)")
                print(f"   - {backup_dir}/ ← 이전 버전 백업")
            
            return result
        
        else:
            print(f"\n❌ 버전 생성 실패: {result.get('error')}")
            return None
    
    except Exception as e:
        print(f"\n❌ 버전 생성 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


async def interactive_run():
    """대화형 실행"""
    print("\n" + "=" * 70)
    print("HR Validation Agent + Auto CMO Versioning")
    print("=" * 70)
    
    # 입력 파일 선택
    input_file = input("\n입력 JSON 파일 (Enter = hr_input_with_actual_performance.json): ").strip()
    if not input_file:
        input_file = "hr_input_with_actual_performance.json"
    
    # 버전 이름
    version_name = input("버전 이름 (Enter = 자동 생성): ").strip()
    if not version_name:
        version_name = None
    
    # 실행 (자동으로 cmo_agent/ 업데이트)
    result = await run_hr_with_auto_versioning(
        input_json_path=input_file,
        version_name=version_name
    )
    
    if result:
        print("\n" + "=" * 70)
        print("✅ 전체 프로세스 완료!")
        print("=" * 70)
        backup_dir = result.get('backup_path', '').split('/')[-1] if result.get('backup_path') else 'cmo_agent_v0'
        
        print("\n다음 단계:")
        print("1. CMO Agent 테스트 (새 프롬프트로):")
        print("   python test_cmo_agent.py")
        print("\n2. 버전 히스토리 조회:")
        print("   ls -la | grep cmo_agent_v")
        print("   또는")
        print("   python -c \"from cmo_agent.tools_version import list_cmo_versions; print(list_cmo_versions())\"")
        print("\n3. 문제 있으면 이전 버전으로 롤백:")
        print(f"   python -c \"from cmo_agent.tools_version import restore_cmo_version; print(restore_cmo_version('{backup_dir}'))\"")
    else:
        print("\n⚠️ 프로세스 중 오류 발생")


async def quick_run_example():
    """빠른 실행 예제 (기본 설정)"""
    result = await run_hr_with_auto_versioning(
        input_json_path="hr_input_with_actual_performance.json",
        version_name=None  # 자동 생성
    )
    return result


def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 빠른 실행
        print("\n🚀 빠른 실행 모드")
        asyncio.run(quick_run_example())
    else:
        # 대화형 실행
        asyncio.run(interactive_run())


if __name__ == "__main__":
    main()

