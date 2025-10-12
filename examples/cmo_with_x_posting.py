"""
CMO Agent - X 포스팅 기능 사용 예제 (OpenTelemetry Weave 통합)

이 예제는 CMO Agent가 콘텐츠를 생성하고 사용자 승인 후 X에 포스팅하는 
전체 워크플로우를 보여줍니다. 모든 ADK 작업이 자동으로 Weave로 추적됩니다.
"""

import sys
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# CMO Agent import (자동으로 OpenTelemetry 설정)
from cmo_agent.agent import root_agent, decide_and_execute


def main():
    """
    CMO Agent 실행 예제
    
    워크플로우:
    1. 콘텐츠 생성 요청
    2. Agent가 자동으로 Research -> 3x Loop -> Safety -> Selection -> Image Generation 실행
    3. 완성된 콘텐츠를 사용자에게 보여주고 승인 요청
    4. 사용자가 "yes" 또는 "포스팅"이라고 답하면 실제로 X에 포스팅
    """
    
    print("=" * 80)
    print("CMO Agent - X 포스팅 기능 데모 (with Weave OTEL)")
    print("=" * 80)
    print()
    
    # 환경 변수 확인
    if not os.getenv('WANDB_API_KEY'):
        print("⚠️  경고: WANDB_API_KEY가 설정되지 않았습니다.")
        print("   Weave traces를 보려면 환경 변수를 설정하세요.\n")
    
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ 에러: GOOGLE_API_KEY가 필요합니다.")
        return
    
    print("💡 TIP: .env 파일에 X API 토큰이 설정되어 있어야 실제 포스팅이 가능합니다.")
    print("    설정이 없으면 시뮬레이션 모드로 동작합니다.")
    print()
    print("🔧 토큰 설정 방법:")
    print("    1. .env 파일에 X API credentials 추가")
    print("    2. python oauth2_setup.py 실행")
    print("    3. 브라우저에서 앱 승인")
    print()
    print("=" * 80)
    print()
    
    # 콘텐츠 생성 요청
    print("📝 콘텐츠 생성을 시작합니다...")
    print("   - 모든 ADK 작업이 Weave로 자동 전송됩니다")
    print()
    
    request = "Give me next content for X/Twitter"
    
    try:
        # Agent 실행 (OpenTelemetry가 자동으로 추적)
        result = decide_and_execute(request)
        
        print()
        print("=" * 80)
        print("✅ 콘텐츠 생성 완료!")
        print("=" * 80)
        print()
        print("Agent의 응답:")
        print(result)
        print()
        
        # Weave 대시보드 링크
        project_id = os.getenv('WANDB_PROJECT_ID', 'mason-choi-storika/WeaveHacks2')
        print("=" * 80)
        print("🐝 Weave 대시보드에서 traces 확인:")
        print(f"   https://wandb.ai/{project_id}")
        print("=" * 80)
        print()
        print("📌 다음 단계:")
        print("   - Agent가 승인을 요청하면 'yes' 또는 '포스팅'이라고 답하세요")
        print("   - 실제 X 포스팅이 진행됩니다")
        print("   - 포스팅 후 트윗 URL이 표시됩니다")
        print()
        
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    

def interactive_mode():
    """
    대화형 모드로 Agent와 상호작용
    """
    print("=" * 80)
    print("CMO Agent - 대화형 모드")
    print("=" * 80)
    print()
    print("명령어:")
    print("  - 'content' 또는 'generate': 새 콘텐츠 생성")
    print("  - 'quit' 또는 'exit': 종료")
    print()
    print("=" * 80)
    print()
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료']:
            print("\n👋 CMO Agent를 종료합니다.")
            break
        
        if not user_input:
            continue
        
        # 콘텐츠 생성 요청 감지
        if user_input.lower() in ['content', 'generate', '콘텐츠', '생성']:
            user_input = "Give me next content for X/Twitter"
        
        print()
        print("🤖 CMO Agent가 작업 중...")
        print("   - OpenTelemetry가 모든 작업을 Weave로 전송합니다")
        print()
        
        try:
            result = decide_and_execute(user_input)
            print(f"Agent: {result}")
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            import traceback
            traceback.print_exc()
        
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CMO Agent X 포스팅 데모")
    parser.add_argument(
        "--interactive", 
        "-i", 
        action="store_true", 
        help="대화형 모드로 실행"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        main()

