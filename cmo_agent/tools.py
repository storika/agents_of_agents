"""
CMO Agent 도구 함수들
"""

import json
import random
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import weave
import requests
from dotenv import load_dotenv
from cmo_agent.schemas import ContentCandidate, EvaluationScores

# OAuth 2.0 설정
TWITTER_API_V2_URL = "https://api.twitter.com/2/tweets"
# Media upload - V2 시도 후 V1.1 fallback
TWITTER_MEDIA_UPLOAD_V2_URL = "https://upload.twitter.com/2/media/upload.json"
TWITTER_MEDIA_UPLOAD_V1_URL = "https://upload.twitter.com/1.1/media/upload.json"


def load_latest_trend_data() -> Optional[Dict[str, Any]]:
    """
    Load the most recent trending data from trend_data/ directory.

    Returns:
        Dict with trend data or None if no data found
    """
    trend_data_dir = Path(__file__).parent.parent / "trend_data"

    if not trend_data_dir.exists():
        print("⚠️ trend_data/ directory not found")
        return None

    # Find most recent trending_*.json file
    trend_files = sorted(trend_data_dir.glob("trending_*.json"), reverse=True)

    if not trend_files:
        print("⚠️ No trend data files found in trend_data/")
        return None

    latest_file = trend_files[0]
    print(f"📊 Loading trend data from: {latest_file.name}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading trend data: {e}")
        return None


@weave.op()
def research_trends(topic: str = "AI agents", max_results: int = 10) -> str:
    """
    트렌드 리서치 수행 - Load real trending data from trend_data/ directory

    Args:
        topic: 조사할 주제 (optional filter, ignored if real data available)
        max_results: 반환할 최대 결과 수

    Returns:
        JSON 형식의 리서치 결과 with trending_topics array
    """
    # Load real trending data
    trend_data = load_latest_trend_data()

    if trend_data:
        # Extract trending topics from the pipeline output
        trending_topics = []

        # Get data from data_sources structure
        data_sources = trend_data.get("data_sources", {})

        # Extract from twitter_trends if available
        if "twitter_trends" in data_sources:
            twitter_trends = data_sources["twitter_trends"]
            if twitter_trends.get("collected"):
                tabs_data = twitter_trends.get("data", {}).get("tabs", {})

                for category, tab_info in tabs_data.items():
                    topics_list = tab_info.get("trending_topics", [])
                    for topic in topics_list[:max_results]:
                        trending_topics.append({
                            "topic_name": topic.get("topic_name", "Unknown"),
                            "source": f"Twitter/{category}",
                            "rank": topic.get("rank", "N/A"),
                            "url": topic.get("url", ""),
                            "engagement_hint": topic.get("engagement_hint", "unknown"),
                            "raw_text": topic.get("raw_text", "")[:200]
                        })

        # Extract from post_analysis if available
        if "post_analysis" in data_sources:
            post_analysis_data = data_sources["post_analysis"]
            if post_analysis_data.get("collected"):
                analysis_data = post_analysis_data.get("data", {})
                for keyword_data in analysis_data.get("keywords", [])[:max_results]:
                    keyword = keyword_data.get("keyword", "")
                    posts = keyword_data.get("posts", [])

                    if posts:
                        # Get the most engaging post
                        top_post = posts[0] if posts else {}
                        trending_topics.append({
                            "topic_name": keyword,
                            "source": "Post Analysis",
                            "post_count": len(posts),
                            "top_post": {
                                "title": top_post.get("title", ""),
                                "url": top_post.get("url", ""),
                                "content": top_post.get("content", "")[:200]
                            }
                        })

        # Limit to max_results
        trending_topics = trending_topics[:max_results]

        result = {
            "status": "success",
            "source": "real_trend_data",
            "timestamp": trend_data.get("timestamp", ""),
            "trending_topics": trending_topics,
            "total_topics": len(trending_topics),
            "insights": f"Loaded {len(trending_topics)} trending topics from real-time data collection"
        }

        print(f"✅ Loaded {len(trending_topics)} real trending topics")
        return json.dumps(result, indent=2, ensure_ascii=False)

    else:
        # Fallback to mock data if no real data available
        print("⚠️ No real trend data available, using fallback")

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
            "status": "fallback",
            "source": "mock_data",
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
def upload_media_v2(oauth2_token: str, image_path: str) -> Optional[str]:
    """미디어 업로드 V2 시도 (OAuth 2.0)"""
    print(f"[INFO] V2 API 시도: {image_path}")
    headers = {"Authorization": f"Bearer {oauth2_token}"}
    
    try:
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(TWITTER_MEDIA_UPLOAD_V2_URL, headers=headers, files=files, timeout=30)
        
        if response.status_code in [200, 201]:
            result = response.json()
            media_id = result.get("media_id_string") or result.get("data", {}).get("media_id_string")
            if media_id:
                print(f"[INFO] V2 미디어 업로드 성공: {media_id}")
                return media_id
        
        print(f"[INFO] V2 API 실패 (status={response.status_code}), V1.1로 fallback")
        return None
    except Exception as e:
        print(f"[INFO] V2 API 에러, V1.1로 fallback")
        return None


@weave.op()
def upload_media_v1(oauth1_creds: dict, image_path: str) -> Optional[str]:
    """미디어 업로드 V1.1 (OAuth 1.0a)"""
    print(f"[INFO] V1.1 API 시도: {image_path}")
    
    if not all(oauth1_creds.values()):
        print(f"[ERROR] OAuth 1.0a credentials 필요 (TW_CONSUMER_KEY, TW_CONSUMER_SECRET, TW_ACCESS_TOKEN, TW_ACCESS_SECRET)")
        return None
    
    try:
        from requests_oauthlib import OAuth1
    except ImportError:
        print(f"[ERROR] requests-oauthlib 필요: pip install requests-oauthlib")
        return None
    
    auth = OAuth1(
        oauth1_creds["consumer_key"],
        oauth1_creds["consumer_secret"],
        oauth1_creds["access_token"],
        oauth1_creds["access_secret"],
        signature_type='auth_header'
    )
    
    try:
        with open(image_path, 'rb') as f:
            files = {'media': f}
            response = requests.post(TWITTER_MEDIA_UPLOAD_V1_URL, auth=auth, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            media_id = result.get("media_id_string")
            if media_id:
                print(f"[INFO] V1.1 미디어 업로드 성공: {media_id}")
                return media_id
        
        print(f"[ERROR] V1.1 API 실패: {response.status_code}")
        return None
    except Exception as e:
        print(f"[ERROR] V1.1 Upload error: {e}")
        return None


@weave.op()
def upload_media_to_x(image_path: str) -> Optional[str]:
    """
    X에 미디어 업로드 (V2 시도 → V1.1 fallback)
    
    Args:
        image_path: 업로드할 이미지 파일 경로
    
    Returns:
        성공 시 media_id_string, 실패 시 None
    """
    load_dotenv()
    
    if not os.path.exists(image_path):
        print(f"[ERROR] 이미지 파일을 찾을 수 없습니다: {image_path}")
        return None
    
    oauth2_token = os.getenv("TW_OAUTH2_ACCESS_TOKEN")
    oauth1_creds = {
        "consumer_key": os.getenv("TW_CONSUMER_KEY"),
        "consumer_secret": os.getenv("TW_CONSUMER_SECRET"),
        "access_token": os.getenv("TW_ACCESS_TOKEN"),
        "access_secret": os.getenv("TW_ACCESS_SECRET")
    }
    
    # 1. V2 API 먼저 시도
    if oauth2_token:
        media_id = upload_media_v2(oauth2_token, image_path)
        if media_id:
            return media_id
    
    # 2. V1.1 API로 fallback
    return upload_media_v1(oauth1_creds, image_path)


@weave.op()
def post_to_x_api(text: str, media_keys: Optional[List[str]] = None, max_retries: int = 3) -> Optional[Dict]:
    """
    실제 Twitter API를 사용해서 트윗 발행 (OAuth 2.0)
    
    Args:
        text: 트윗 텍스트
        media_keys: 첨부할 미디어의 media_key 리스트 (선택사항)
        max_retries: 최대 재시도 횟수
    
    Returns:
        성공 시 트윗 데이터, 실패 시 None
    """
    load_dotenv()
    access_token = os.getenv("TW_OAUTH2_ACCESS_TOKEN")
    
    if not access_token:
        print("[WARN] TW_OAUTH2_ACCESS_TOKEN이 설정되지 않았습니다. 시뮬레이션 모드로 동작합니다.")
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    payload = {"text": text}
    
    # 미디어가 있으면 추가
    if media_keys:
        payload["media"] = {"media_ids": media_keys}
    
    delay = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                TWITTER_API_V2_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 201:
                # 성공
                data = response.json()
                return data.get("data", {})
            elif response.status_code == 403:
                print(f"[ERROR] 403 Forbidden - X API 권한 문제")
                print("oauth2_setup.py를 실행하여 새 토큰을 발급받으세요.")
                return None
            elif response.status_code == 429:
                # Rate limit
                if attempt == max_retries:
                    print(f"[ERROR] Rate limit 초과: {response.text}")
                    return None
                print(f"[WARN] Rate limited. Retry in {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                # 다른 오류
                if attempt == max_retries:
                    print(f"[ERROR] HTTP {response.status_code}: {response.text}")
                    return None
                print(f"[WARN] HTTP {response.status_code}. Retry in {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                print(f"[ERROR] Request error: {e}")
                return None
            print(f"[WARN] Request error: {e}. Retry in {delay}s (attempt {attempt}/{max_retries})")
            time.sleep(delay)
            delay *= 2
    
    return None


@weave.op()
def x_publish(
    text: str,
    media_prompt: str = "",
    image_path: Optional[str] = None,
    mode: str = "image",
    require_approval: bool = False,
    actually_post: bool = True
) -> str:
    """
    Twitter/X에 발행 (이미지 포함 가능)
    
    Args:
        text: 포스트 텍스트
        media_prompt: 미디어 생성 프롬프트 (참고용)
        image_path: 업로드할 이미지 파일 경로 (선택사항)
        mode: 미디어 타입
        require_approval: 승인 필요 여부
        actually_post: 실제로 포스팅할지 여부 (False면 시뮬레이션)
    
    Returns:
        JSON 형식의 발행 상태
    
    워크플로우:
        1. 이미지가 있으면 먼저 X Media API v2로 업로드
        2. media_key를 받음
        3. 트윗 생성 시 media_key 포함
    
    Reference:
        https://docs.x.com/x-api/media/upload-media
    """
    
    # 승인 필요한 경우 큐에 추가만
    if require_approval:
        result = {
            "status": "queued",
            "post_id": f"queued_{datetime.now().timestamp()}",
            "text": text,
            "media_prompt": media_prompt,
            "image_path": image_path,
            "mode": mode,
            "scheduled_time": datetime.now().isoformat(),
            "requires_approval": True,
            "message": "승인 대기 중입니다. actually_post=True로 설정하면 자동 발행됩니다."
        }
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    # 실제 포스팅
    if actually_post:
        media_keys = None
        
        # 1단계: 이미지 업로드 (명시적으로 필수 처리)
        if image_path:
            print(f"[INFO] ==========================================")
            print(f"[INFO] 미디어 업로드 시작: {image_path}")
            print(f"[INFO] ==========================================")
            
            # 파일 존재 여부 확인
            if not os.path.exists(image_path):
                print(f"[ERROR] 이미지 파일을 찾을 수 없습니다: {image_path}")
                result = {
                    "status": "failed",
                    "post_id": None,
                    "text": text,
                    "media_prompt": media_prompt,
                    "image_path": image_path,
                    "mode": mode,
                    "error": "Image file not found",
                    "message": f"❌ 이미지 파일을 찾을 수 없어 포스팅이 중단되었습니다: {image_path}"
                }
                return json.dumps(result, indent=2, ensure_ascii=False)
            
            # 미디어 업로드 시도
            print(f"[INFO] upload_media_to_x() 호출 중...")
            media_key = upload_media_to_x(image_path)
            
            if media_key:
                media_keys = [media_key]
                print(f"[INFO] ==========================================")
                print(f"[INFO] ✅ 미디어 업로드 성공: {media_key}")
                print(f"[INFO] ==========================================")
            else:
                # 이미지 업로드 실패 시 포스팅 중단 (명시적)
                print(f"[ERROR] ==========================================")
                print(f"[ERROR] ❌ 미디어 업로드 실패")
                print(f"[ERROR] 포스팅을 중단합니다.")
                print(f"[ERROR] ==========================================")
                result = {
                    "status": "failed",
                    "post_id": None,
                    "text": text,
                    "media_prompt": media_prompt,
                    "image_path": image_path,
                    "mode": mode,
                    "error": "Media upload failed - check OAuth credentials",
                    "message": "❌ 이미지 업로드 실패로 포스팅이 중단되었습니다. OAuth 1.0a credentials를 확인하세요."
                }
                return json.dumps(result, indent=2, ensure_ascii=False)
        
        # 2단계: 트윗 생성 (media_key 포함)
        print(f"[INFO] 트윗 발행 중...")
        if media_keys:
            print(f"[INFO] 미디어 첨부: {media_keys}")
        tweet_data = post_to_x_api(text, media_keys=media_keys)
        
        if tweet_data:
            # 성공
            result = {
                "status": "published",
                "post_id": tweet_data.get("id", "unknown"),
                "text": text,
                "media_prompt": media_prompt,
                "image_path": image_path,
                "media_included": media_keys is not None,
                "mode": mode,
                "published_time": datetime.now().isoformat(),
                "requires_approval": False,
                "message": "✅ 성공적으로 X에 발행되었습니다!" + (" (이미지 포함)" if media_keys else ""),
                "tweet_url": f"https://twitter.com/i/web/status/{tweet_data.get('id', '')}" if tweet_data.get('id') else None
            }
        else:
            # 실패 - 시뮬레이션 모드로 대체
            result = {
                "status": "simulated",
                "post_id": f"sim_{datetime.now().timestamp()}",
                "text": text,
                "media_prompt": media_prompt,
                "image_path": image_path,
                "mode": mode,
                "scheduled_time": datetime.now().isoformat(),
                "requires_approval": False,
                "message": "⚠️ 실제 발행 실패. 시뮬레이션 모드로 처리되었습니다."
            }
    else:
        # 시뮬레이션 모드
        result = {
            "status": "simulated",
            "post_id": f"sim_{datetime.now().timestamp()}",
            "text": text,
            "media_prompt": media_prompt,
            "image_path": image_path,
            "mode": mode,
            "scheduled_time": datetime.now().isoformat(),
            "requires_approval": False,
            "message": "시뮬레이션 모드입니다. actually_post=True로 설정하면 실제 발행됩니다."
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

