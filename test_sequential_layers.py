#!/usr/bin/env python3
"""
CMO Agent - Sequential Layers 테스트 스크립트
5개 레이어를 순차적으로 실행하여 콘텐츠 생성 프로세스 테스트
"""

import json
import sys
from cmo_agent.agent import orchestrate_sequential_layers


def main():
    print("🚀 CMO Agent - Sequential Layers 테스트")
    print("=" * 80)
    
    # 기본 설정
    topic = "AI agents that hire other AI agents"
    audience_demographics = "developers, tech enthusiasts, indie hackers"
    
    # CLI 인자로 주제 변경 가능
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    
    print(f"\n📝 설정:")
    print(f"  주제: {topic}")
    print(f"  청중: {audience_demographics}")
    print(f"  임계값: 기본값 사용 (clarity=0.55, novelty=0.55, shareability=0.55, credibility=0.60, safety=0.80)")
    print()
    
    # Sequential layers 실행
    try:
        result_json = orchestrate_sequential_layers(
            topic=topic,
            audience_demographics=audience_demographics
        )
        
        result = json.loads(result_json)
        
        # 결과 출력
        print("\n" + "=" * 80)
        print("📊 최종 결과")
        print("=" * 80)
        
        status = result.get("status", "unknown")
        print(f"\n상태: {status}")
        
        if status == "approved":
            print("\n✅ 콘텐츠가 승인되었습니다!")
            
            final_scores = result.get("final_scores", {})
            thresholds = result.get("thresholds", {})
            print(f"\n최종 점수:")
            for metric, score in final_scores.items():
                threshold = thresholds.get(metric, 0)
                status_icon = "✅" if score >= threshold else "❌"
                print(f"  {status_icon} {metric}: {score:.2f} (threshold: {threshold})")
            
            # 생성된 콘텐츠 출력
            generator_output = result.get("generator_output", {})
            content_pieces = generator_output.get("content_pieces", [])
            
            if content_pieces:
                print(f"\n생성된 콘텐츠:")
                for i, piece in enumerate(content_pieces):
                    print(f"\n  [{i+1}] {piece.get('platform', 'N/A')} - {piece.get('format', 'N/A')}")
                    print(f"  콘텐츠: {piece.get('content', '')}")
                    print(f"  해시태그: {', '.join(piece.get('hashtags', []))}")
                    if piece.get('call_to_action'):
                        print(f"  CTA: {piece.get('call_to_action', '')}")
        
        elif status == "rejected":
            reason = result.get("reason", "unknown")
            print(f"\n❌ 콘텐츠가 거부되었습니다: {reason}")
            
            safety_output = result.get("safety_output", {})
            red_flags = safety_output.get("red_flags", [])
            
            if red_flags:
                print(f"\n위험 플래그:")
                for flag in red_flags:
                    print(f"  - [{flag.get('category', '')}] {flag.get('description', '')}")
                    print(f"    심각도: {flag.get('severity', '')}")
        
        elif status == "needs_improvement":
            print(f"\n⚠️ 콘텐츠가 품질 기준을 충족하지 못했습니다")
            
            final_scores = result.get("final_scores", {})
            thresholds = result.get("thresholds", {})
            print(f"\n점수:")
            for metric, score in final_scores.items():
                threshold = thresholds.get(metric, 0)
                status_icon = "✅" if score >= threshold else "❌"
                print(f"  {status_icon} {metric}: {score:.2f} (threshold: {threshold})")
        
        elif "error" in result:
            print(f"\n❌ 오류 발생: {result['error']}")
            if "traceback" in result:
                print(f"\n상세 오류:\n{result['traceback']}")
        
        # 결과를 파일로 저장
        output_file = "sequential_layers_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 전체 결과가 {output_file}에 저장되었습니다.")
        
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

