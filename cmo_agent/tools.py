"""
CMO Agent 도구 함수들
"""

import json
import random
from typing import Dict, List, Any
from datetime import datetime
import weave
from cmo_agent.schemas import ContentCandidate, EvaluationScores


@weave.op()
def research_trends(topic: str = "AI agents", max_results: int = 3) -> str:
    """
    트렌드 리서치 수행
    
    Args:
        topic: 조사할 주제
        max_results: 반환할 최대 결과 수
    
    Returns:
        JSON 형식의 리서치 결과
    """
    # 실제로는 TrendScout 에이전트를 호출하거나 Twitter API를 사용
    # 여기서는 시뮬레이션
    
    trending_keywords = [
        "AI", "agents", "automation", "LLM", "GPT", "Claude",
        "developers", "builders", "indie hackers", "startups"
    ]
    
    sample_topics = [
        f"{topic}와 자동화의 미래",
        f"{topic} 개발자 경험 개선",
        f"{topic}가 바꾸는 워크플로우"
    ]
    
    result = {
        "topics": random.sample(sample_topics, min(max_results, len(sample_topics))),
        "keywords": random.sample(trending_keywords, min(5, len(trending_keywords))),
        "tone_style": "conversational, builder-friendly",
        "insights": f"{topic}에 대한 개발자들의 관심이 증가하고 있습니다. 실용적이고 구체적인 사례를 선호합니다."
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)


@weave.op()
def generate_content_candidate(
    topic: str,
    tone: str = "conversational",
    max_length: int = 180
) -> str:
    """
    콘텐츠 후보 생성 (Writer 에이전트 시뮬레이션)
    
    Args:
        topic: 콘텐츠 주제
        tone: 톤/스타일
        max_length: 최대 텍스트 길이
    
    Returns:
        JSON 형식의 콘텐츠 후보
    """
    
    # 실제로는 ViralCopywriter, Hooksmith 등 서브 에이전트 호출
    # 여기서는 템플릿 기반 생성
    
    hooks = [
        f"우리는 {topic}를 만들었습니다.",
        f"{topic}로 팀을 자동화하는 방법",
        f"왜 모든 개발자가 {topic}를 사용해야 하는가",
        f"{topic}의 미래는 이미 여기에 있습니다",
    ]
    
    text = random.choice(hooks)
    
    candidate = {
        "text": text[:max_length],
        "media_prompt": f"3D isometric illustration of {topic}, modern tech aesthetic, vibrant colors",
        "mode": random.choice(["image", "image", "gif"]),  # image 확률 높게
        "expected_engagement": round(random.uniform(0.6, 0.9), 2)
    }
    
    return json.dumps(candidate, indent=2, ensure_ascii=False)


@weave.op()
def evaluate_content(
    text: str,
    media_prompt: str
) -> str:
    """
    콘텐츠 평가 (Critic + Safety 에이전트 시뮬레이션)
    
    Args:
        text: 평가할 텍스트
        media_prompt: 미디어 프롬프트
    
    Returns:
        JSON 형식의 평가 점수
    """
    
    # 실제로는 Critic, Safety 에이전트를 병렬로 호출
    # 여기서는 규칙 기반 + 랜덤 점수
    
    # 기본 점수 (0.5~0.9 사이)
    base_score = 0.7
    
    # 텍스트 길이에 따른 clarity 조정
    clarity = base_score + (0.2 if len(text) < 200 else 0.0)
    clarity = min(clarity, 1.0)
    
    # 키워드 기반 novelty
    novelty_keywords = ["AI", "agents", "automation", "future"]
    novelty = base_score + (0.1 if any(kw.lower() in text.lower() for kw in novelty_keywords) else 0.0)
    
    # shareability는 짧고 임팩트 있으면 높음
    shareability = base_score + (0.15 if len(text) < 150 else 0.0)
    shareability = min(shareability, 1.0)
    
    # credibility는 대부분 양호
    credibility = 0.75 + random.uniform(0, 0.15)
    
    # safety는 거의 항상 높음 (문제 있는 콘텐츠는 사전 필터링)
    safety = 0.95 + random.uniform(0, 0.05)
    
    scores = EvaluationScores(
        clarity=round(clarity, 2),
        novelty=round(novelty, 2),
        shareability=round(shareability, 2),
        credibility=round(credibility, 2),
        safety=round(safety, 2),
        overall=0.0  # 나중에 계산
    )
    
    # overall 계산
    weights = {
        "clarity": 0.25,
        "novelty": 0.25,
        "shareability": 0.30,
        "credibility": 0.10,
        "safety": 0.10
    }
    
    overall = sum(
        getattr(scores, metric) * weight 
        for metric, weight in weights.items()
    )
    scores.overall = round(overall, 2)
    
    return scores.model_dump_json(indent=2)


@weave.op()
def x_publish(
    text: str,
    media_prompt: str,
    mode: str = "image",
    require_approval: bool = True
) -> str:
    """
    Twitter/X에 발행
    
    Args:
        text: 포스트 텍스트
        media_prompt: 미디어 생성 프롬프트
        mode: 미디어 타입
        require_approval: 승인 필요 여부
    
    Returns:
        JSON 형식의 발행 상태
    """
    
    # 실제로는 Twitter API 호출
    # 여기서는 시뮬레이션
    
    status = "queued" if require_approval else "published"
    
    result = {
        "status": status,
        "post_id": f"sim_{datetime.now().timestamp()}",
        "text": text,
        "media_prompt": media_prompt,
        "mode": mode,
        "scheduled_time": datetime.now().isoformat(),
        "requires_approval": require_approval,
        "message": "승인 대기 중입니다." if require_approval else "발행되었습니다."
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)


@weave.op()
def get_last_iteration_metrics(filepath: str = "last_iteration.json") -> str:
    """
    이전 반복의 메트릭 로드
    
    Args:
        filepath: 메트릭 파일 경로
    
    Returns:
        JSON 형식의 메트릭
    """
    try:
        import os
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
        else:
            return json.dumps({
                "iteration": 0,
                "top_post": None,
                "engagement": {"likes": 0, "reposts": 0, "comments": 0}
            }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@weave.op()
def save_iteration_metrics(
    iteration: int,
    selected_candidate: Dict[str, Any],
    predicted_score: float,
    filepath: str = "last_iteration.json"
) -> str:
    """
    현재 반복 메트릭 저장
    
    Args:
        iteration: 반복 번호
        selected_candidate: 선택된 후보
        predicted_score: 예상 점수
        filepath: 저장 경로
    
    Returns:
        저장 상태 메시지
    """
    try:
        data = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "selected_candidate": selected_candidate,
            "predicted_score": predicted_score,
            "engagement": {"likes": 0, "reposts": 0, "comments": 0}  # 나중에 업데이트
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return json.dumps({"status": "success", "message": f"메트릭이 {filepath}에 저장되었습니다."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

