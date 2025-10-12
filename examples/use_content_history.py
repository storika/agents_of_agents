"""
이전 컨텐츠 결과와 트렌드 데이터를 사용하는 예제
"""

import json
from pathlib import Path


def load_content_history(filepath: str = "examples/content_history_sample.json") -> dict:
    """
    이전 컨텐츠 히스토리 로드
    
    Args:
        filepath: 히스토리 파일 경로
    
    Returns:
        컨텐츠 히스토리 딕셔너리
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_context_for_research(history_data: dict) -> str:
    """
    Research Agent에 제공할 컨텍스트 포맷팅
    
    Args:
        history_data: 로드된 히스토리 데이터
    
    Returns:
        포맷팅된 컨텍스트 문자열
    """
    trends = history_data.get('performance_trends', {})
    current_trends = history_data.get('current_trends', {})
    
    context = f"""
=== PREVIOUS CONTENT PERFORMANCE ===

Top Performing Content Types:
{json.dumps(trends.get('top_performing_characteristics', {}).get('content_types', []), indent=2)}

Audience Insights:
{json.dumps(trends.get('audience_insights', {}), indent=2)}

Key Recommendations:
"""
    for rec in trends.get('recommendations', []):
        context += f"- {rec}\n"
    
    context += f"""

=== CURRENT TRENDS (as of {current_trends.get('date', 'N/A')}) ===

Platform Trends:
{json.dumps(current_trends.get('platform_trends', {}), indent=2)}

Emerging Topics:
{json.dumps(current_trends.get('emerging_topics', []), indent=2)}

Use this historical performance data and current trends to inform your research and content recommendations.
"""
    
    return context


def get_best_performing_posts(history_data: dict, top_n: int = 3) -> list:
    """
    최고 성과 게시물 추출
    
    Args:
        history_data: 히스토리 데이터
        top_n: 상위 N개
    
    Returns:
        상위 게시물 리스트
    """
    posts = history_data.get('content_history', [])
    
    # Engagement rate 기준으로 정렬
    sorted_posts = sorted(
        posts, 
        key=lambda x: x.get('actual_performance', {}).get('engagement_rate', 0),
        reverse=True
    )
    
    return sorted_posts[:top_n]


def analyze_performance_patterns(history_data: dict) -> dict:
    """
    성과 패턴 분석
    
    Args:
        history_data: 히스토리 데이터
    
    Returns:
        분석 결과
    """
    posts = history_data.get('content_history', [])
    
    # 점수와 실제 성과의 상관관계 분석
    correlations = {
        'predicted_vs_actual': [],
        'best_predictor_score': None,
        'insights': []
    }
    
    for post in posts:
        predicted = post.get('scores', {}).get('overall', 0)
        actual = post.get('actual_performance', {}).get('engagement_rate', 0)
        correlations['predicted_vs_actual'].append({
            'post_id': post.get('id'),
            'predicted_score': predicted,
            'actual_engagement': actual,
            'difference': abs(predicted - actual * 10)  # Normalize to 0-1 scale
        })
    
    # 가장 예측이 정확했던 점수 찾기
    avg_diff = sum(c['difference'] for c in correlations['predicted_vs_actual']) / len(correlations['predicted_vs_actual'])
    correlations['avg_prediction_error'] = avg_diff
    
    # 인사이트 생성
    trends = history_data.get('performance_trends', {})
    top_chars = trends.get('top_performing_characteristics', {})
    
    if top_chars:
        best_type = top_chars.get('content_types', [{}])[0]
        correlations['insights'].append(
            f"Best performing content type: {best_type.get('type', 'N/A')} "
            f"(avg engagement: {best_type.get('avg_engagement', 0):.3f})"
        )
    
    return correlations


def main():
    """메인 실행 예제"""
    
    print("="*70)
    print("Content History Analysis Example")
    print("="*70)
    
    # 1. 히스토리 로드
    history = load_content_history()
    print(f"\n✓ Loaded {len(history.get('content_history', []))} historical posts")
    
    # 2. 최고 성과 게시물
    print("\n" + "="*70)
    print("TOP PERFORMING POSTS")
    print("="*70)
    top_posts = get_best_performing_posts(history, top_n=3)
    
    for i, post in enumerate(top_posts, 1):
        perf = post.get('actual_performance', {})
        print(f"\n{i}. {post.get('id')} - {post.get('date')}")
        print(f"   Text: {post.get('content', {}).get('text', '')[:80]}...")
        print(f"   Engagement Rate: {perf.get('engagement_rate', 0):.3f}")
        print(f"   Views: {perf.get('views', 0):,}")
        print(f"   Feedback: {post.get('feedback', 'N/A')}")
    
    # 3. 성과 패턴 분석
    print("\n" + "="*70)
    print("PERFORMANCE PATTERN ANALYSIS")
    print("="*70)
    patterns = analyze_performance_patterns(history)
    
    print(f"\nAverage Prediction Error: {patterns.get('avg_prediction_error', 0):.3f}")
    print("\nKey Insights:")
    for insight in patterns.get('insights', []):
        print(f"  • {insight}")
    
    # 4. Research Agent용 컨텍스트
    print("\n" + "="*70)
    print("RESEARCH AGENT CONTEXT")
    print("="*70)
    context = format_context_for_research(history)
    print(context[:500] + "...\n[truncated for display]")
    
    # 5. 전체 컨텍스트 저장
    output_file = "examples/research_context.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(context)
    print(f"\n✓ Full context saved to: {output_file}")
    
    # 6. 권장사항 요약
    print("\n" + "="*70)
    print("KEY RECOMMENDATIONS FOR NEXT CONTENT")
    print("="*70)
    recommendations = history.get('performance_trends', {}).get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print("\n" + "="*70)
    print("✨ Analysis Complete!")
    print("="*70)


if __name__ == "__main__":
    main()

