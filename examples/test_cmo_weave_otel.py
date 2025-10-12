"""
CMO Agent with OpenTelemetry Weave Integration Test

이 예제는 Google ADK와 Weave의 OpenTelemetry 통합을 보여줍니다.
Reference: https://google.github.io/adk-docs/observability/weave/

필수 환경 변수:
- WANDB_API_KEY: W&B API key (https://wandb.ai/authorize)
- GOOGLE_API_KEY: Google API key
- WANDB_PROJECT_ID: (선택) W&B 프로젝트 (기본값: mason-choi-storika/WeaveHacks2)
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Import CMO Agent
# IMPORTANT: cmo_agent를 import하면 자동으로 OpenTelemetry가 설정됩니다.
# 이는 ADK를 사용하기 전에 tracer provider를 설정하기 위함입니다.
from cmo_agent.agent import root_agent

async def test_basic_request():
    """기본 요청 테스트 - Weave traces 확인용"""
    print("\n" + "="*60)
    print("테스트: CMO Agent with OpenTelemetry Weave Integration")
    print("="*60)
    
    # 간단한 요청으로 트렌드 컨텍스트 가져오기
    user_request = "오늘의 트렌드를 기반으로 quote tweet을 만들어줘"
    
    print(f"\n📝 사용자 요청: {user_request}")
    print("\n⏳ CMO Agent 실행 중...")
    print("   - OpenTelemetry traces가 Weave로 전송됩니다")
    print("   - Weave 대시보드에서 실시간으로 확인 가능합니다\n")
    
    try:
        # Set up runner
        runner = InMemoryRunner(agent=root_agent, app_name="cmo_agent")
        session_service = runner.session_service
        
        # Create a session
        user_id = "test_user"
        session_id = "test_session"
        await session_service.create_session(
            app_name="cmo_agent",
            user_id=user_id,
            session_id=session_id,
        )
        
        # Run the agent
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=user_request)]
            ),
        ):
            if event.is_final_response() and event.content:
                response = event.content.parts[0].text.strip()
                print("\n✅ CMO Agent 실행 완료!")
                print(f"\n📊 응답:\n{response}")
        
        print("\n" + "="*60)
        print("🐝 Weave 대시보드에서 traces를 확인하세요:")
        print("   URL: https://wandb.ai/mason-choi-storika/WeaveHacks2")
        print("   - Traces 탭 클릭")
        print("   - Timeline View에서 실행 흐름 분석")
        print("   - 각 LLM call과 tool invocation 확인")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        print("\n디버깅 팁:")
        print("1. WANDB_API_KEY가 설정되었는지 확인")
        print("2. GOOGLE_API_KEY가 설정되었는지 확인")
        print("3. 인터넷 연결 확인")
        raise

def test_trending_only():
    """트렌드 정보만 가져오기 테스트"""
    print("\n" + "="*60)
    print("테스트: 트렌드 정보 조회")
    print("="*60)
    
    user_request = "현재 트렌드를 알려줘"
    
    print(f"\n📝 사용자 요청: {user_request}")
    
    try:
        response = decide_and_execute(user_request)
        print(f"\n✅ 응답:\n{response}")
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        raise

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 환경 변수 확인")
    print("="*60)
    
    # 필수 환경 변수 확인
    wandb_key = os.getenv('WANDB_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    project_id = os.getenv('WANDB_PROJECT_ID', 'mason-choi-storika/WeaveHacks2')
    
    print(f"   WANDB_API_KEY: {'✅ 설정됨' if wandb_key else '❌ 없음'}")
    print(f"   GOOGLE_API_KEY: {'✅ 설정됨' if google_key else '❌ 없음'}")
    print(f"   WANDB_PROJECT_ID: {project_id}")
    
    if not wandb_key or not google_key:
        print("\n❌ 에러: 필수 환경 변수가 설정되지 않았습니다.")
        print("\n설정 방법:")
        print("   1. .env 파일 생성:")
        print("      echo 'WANDB_API_KEY=your_key' >> .env")
        print("      echo 'GOOGLE_API_KEY=your_key' >> .env")
        print("\n   2. 또는 환경 변수로 export:")
        print("      export WANDB_API_KEY=your_key")
        print("      export GOOGLE_API_KEY=your_key")
        print("\n   W&B API Key: https://wandb.ai/authorize")
        exit(1)
    
    print("\n✅ 모든 필수 환경 변수가 설정되었습니다.")
    print(f"\n📡 Weave 프로젝트: {project_id}")
    print(f"   대시보드: https://wandb.ai/{project_id}")
    
    try:
        # 기본 테스트 실행
        test_basic_request()
        
        # 추가 테스트 (선택)
        # test_trending_only()
        
    except ValueError as e:
        print(f"\n❌ 설정 에러: {e}")
        print("\n환경 변수를 확인하고 다시 시도하세요.")
        exit(1)
    except Exception as e:
        print(f"\n❌ 실행 에러: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

