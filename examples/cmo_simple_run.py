"""
CMO Agent 간단한 실행 예제 (OpenTelemetry Weave 통합)

이 예제는 CMO Agent를 사용하여 콘텐츠를 생성하고,
모든 ADK 작업이 자동으로 Weave로 추적되는 것을 보여줍니다.
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# CMO Agent import (자동으로 OpenTelemetry 설정)
from cmo_agent.agent import root_agent, decide_and_execute


def main():
    """CMO 에이전트 실행 예제"""
    
    print("🚀 CMO Agent 실행 예제 (with Weave OpenTelemetry)")
    print("=" * 70 + "\n")
    
    # 환경 변수 확인
    if not os.getenv('WANDB_API_KEY'):
        print("⚠️  경고: WANDB_API_KEY가 설정되지 않았습니다.")
        print("   Weave traces를 보려면 환경 변수를 설정하세요.")
        print("   export WANDB_API_KEY=your_key\n")
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ 에러: GOOGLE_API_KEY가 필요합니다.")
        print("   export GOOGLE_API_KEY=your_key")
        return
    
    # 요청 설정
    user_request = "AI agents that hire other AI agents for WeaveHack2에 대한 quote tweet을 만들어줘"
    
    print(f"📝 요청: {user_request}\n")
    print("⏳ CMO Agent 실행 중...")
    print("   - 트렌드 조사")
    print("   - 콘텐츠 생성")
    print("   - 모든 작업이 Weave로 자동 전송됨\n")
    
    try:
        # CMO 실행
        response = decide_and_execute(user_request)
        
        # 결과 출력
        print("\n" + "=" * 70)
        print("📊 실행 결과")
        print("=" * 70 + "\n")
        print(response)
        
        # Weave 대시보드 링크
        project_id = os.getenv('WANDB_PROJECT_ID', 'mason-choi-storika/WeaveHacks2')
        print("\n" + "=" * 70)
        print("🐝 Weave 대시보드에서 traces 확인:")
        print(f"   https://wandb.ai/{project_id}")
        print("   - Traces 탭에서 실행 흐름 확인")
        print("   - Timeline View에서 각 단계별 latency 분석")
        print("   - LLM 호출과 tool invocation 추적")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()

