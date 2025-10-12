"""
CMO Agent - X 포스팅 기능 사용 예제

이 예제는 CMO Agent가 콘텐츠를 생성하고 사용자 승인 후 X에 포스팅하는 전체 워크플로우를 보여줍니다.
"""

import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cmo_agent.agent import root_agent


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
    print("CMO Agent - X 포스팅 기능 데모")
    print("=" * 80)
    print()
    print("💡 TIP: .env 파일에 TW_OAUTH2_ACCESS_TOKEN이 설정되어 있어야 실제 포스팅이 가능합니다.")
    print("    설정이 없으면 시뮬레이션 모드로 동작합니다.")
    print()
    print("🔧 토큰 설정 방법:")
    print("    1. .env 파일에 TW_CLIENT_ID와 TW_CLIENT_SECRET 추가")
    print("    2. python oauth2_setup.py 실행")
    print("    3. 브라우저에서 앱 승인")
    print()
    print("=" * 80)
    print()
    
    # 콘텐츠 생성 요청
    print("📝 콘텐츠 생성을 시작합니다...")
    print()
    
    request = "Give me next content for X/Twitter"
    
    # Agent 실행
    result = root_agent.run(request)
    
    print()
    print("=" * 80)
    print("✅ 콘텐츠 생성 완료!")
    print("=" * 80)
    print()
    print("Agent의 응답:")
    print(result)
    print()
    print("=" * 80)
    print()
    print("📌 다음 단계:")
    print("   - Agent가 승인을 요청하면 'yes' 또는 '포스팅'이라고 답하세요")
    print("   - 실제 X 포스팅이 진행됩니다")
    print("   - 포스팅 후 트윗 URL이 표시됩니다")
    print()
    

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
        print()
        
        try:
            result = root_agent.run(user_input)
            print(f"Agent: {result}")
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
        
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

