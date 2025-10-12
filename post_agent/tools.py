"""
Post Agent Tools - X Publishing and Media Upload
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import weave
import requests
from dotenv import load_dotenv

# Twitter API URLs
TWITTER_API_V2_URL = "https://api.twitter.com/2/tweets"
TWITTER_MEDIA_UPLOAD_V2_URL = "https://upload.twitter.com/2/media/upload.json"
TWITTER_MEDIA_UPLOAD_V1_URL = "https://upload.twitter.com/1.1/media/upload.json"


@weave.op()
def upload_media_v2(oauth2_token: str, image_path: str) -> Optional[str]:
    """Upload media using Twitter API V2 (OAuth 2.0)"""
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
        print(f"[INFO] V2 API 에러, V1.1로 fallback: {e}")
        return None


@weave.op()
def upload_media_v1(oauth1_creds: dict, image_path: str) -> Optional[str]:
    """Upload media using Twitter API V1.1 (OAuth 1.0a)"""
    print(f"[INFO] V1.1 API 시도: {image_path}")

    if not all(oauth1_creds.values()):
        print(f"[ERROR] OAuth 1.0a credentials 필요")
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
    Upload media to X (V2 attempt → V1.1 fallback)

    Args:
        image_path: Path to image file

    Returns:
        media_id_string on success, None on failure
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

    # Try V2 API first
    if oauth2_token:
        media_id = upload_media_v2(oauth2_token, image_path)
        if media_id:
            return media_id

    # Fallback to V1.1 API
    return upload_media_v1(oauth1_creds, image_path)


@weave.op()
def post_to_x_api(text: str, media_keys: Optional[List[str]] = None, max_retries: int = 3) -> Optional[Dict]:
    """
    Post tweet using Twitter API V2 (OAuth 2.0)

    Args:
        text: Tweet text
        media_keys: List of media_id_string to attach
        max_retries: Maximum retry attempts

    Returns:
        Tweet data on success, None on failure
    """
    load_dotenv()
    access_token = os.getenv("TW_OAUTH2_ACCESS_TOKEN")

    if not access_token:
        print("[WARN] TW_OAUTH2_ACCESS_TOKEN not set. Running in simulation mode.")
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {"text": text}

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
                data = response.json()
                return data.get("data", {})
            elif response.status_code == 403:
                print(f"[ERROR] 403 Forbidden - X API 권한 문제")
                return None
            elif response.status_code == 429:
                if attempt == max_retries:
                    print(f"[ERROR] Rate limit 초과")
                    return None
                print(f"[WARN] Rate limited. Retry in {delay}s")
                time.sleep(delay)
                delay *= 2
            else:
                if attempt == max_retries:
                    print(f"[ERROR] HTTP {response.status_code}: {response.text}")
                    return None
                time.sleep(delay)
                delay *= 2
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                print(f"[ERROR] Request error: {e}")
                return None
            time.sleep(delay)
            delay *= 2

    return None


@weave.op()
def x_publish(
    text: str,
    image_path: Optional[str] = None,
    actually_post: bool = True,
    require_approval: bool = False
) -> str:
    """
    Publish to Twitter/X with optional image

    Args:
        text: Tweet text
        image_path: Path to image file (optional)
        actually_post: If True, actually post; if False, simulate
        require_approval: If True, queue for approval

    Returns:
        JSON string with posting status

    Workflow:
        1. If image provided, upload to X Media API (V2 → V1.1 fallback)
        2. Get media_id
        3. Post tweet with media_id attached
    """

    # If approval required, queue only
    if require_approval:
        result = {
            "status": "queued",
            "post_id": f"queued_{datetime.now().timestamp()}",
            "text": text,
            "image_path": image_path,
            "scheduled_time": datetime.now().isoformat(),
            "requires_approval": True,
            "message": "승인 대기 중입니다."
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    # Actually post
    if actually_post:
        media_keys = None

        # Step 1: Upload image if provided
        if image_path:
            print(f"[INFO] ==========================================")
            print(f"[INFO] 미디어 업로드 시작: {image_path}")
            print(f"[INFO] ==========================================")

            if not os.path.exists(image_path):
                result = {
                    "status": "failed",
                    "error": "Image file not found",
                    "image_path": image_path,
                    "message": f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}"
                }
                return json.dumps(result, indent=2, ensure_ascii=False)

            media_key = upload_media_to_x(image_path)

            if media_key:
                media_keys = [media_key]
                print(f"[INFO] ✅ 미디어 업로드 성공: {media_key}")
            else:
                print(f"[ERROR] ❌ 미디어 업로드 실패")
                result = {
                    "status": "failed",
                    "error": "Media upload failed",
                    "image_path": image_path,
                    "message": "❌ 이미지 업로드 실패로 포스팅이 중단되었습니다."
                }
                return json.dumps(result, indent=2, ensure_ascii=False)

        # Step 2: Post tweet
        print(f"[INFO] 트윗 발행 중...")
        tweet_data = post_to_x_api(text, media_keys=media_keys)

        if tweet_data:
            result = {
                "status": "published",
                "post_id": tweet_data.get("id", "unknown"),
                "text": text,
                "image_path": image_path,
                "media_included": media_keys is not None,
                "published_time": datetime.now().isoformat(),
                "message": "✅ 성공적으로 X에 발행되었습니다!",
                "tweet_url": f"https://twitter.com/i/web/status/{tweet_data.get('id', '')}"
            }
        else:
            result = {
                "status": "simulated",
                "post_id": f"sim_{datetime.now().timestamp()}",
                "text": text,
                "image_path": image_path,
                "message": "⚠️ 실제 발행 실패. 시뮬레이션 모드로 처리되었습니다."
            }
    else:
        # Simulation mode
        result = {
            "status": "simulated",
            "post_id": f"sim_{datetime.now().timestamp()}",
            "text": text,
            "image_path": image_path,
            "scheduled_time": datetime.now().isoformat(),
            "message": "시뮬레이션 모드입니다."
        }

    return json.dumps(result, indent=2, ensure_ascii=False)


def post_to_x(text: str, image_path: str = "", hashtags: str = "", actually_post: bool = True) -> str:
    """
    Wrapper for ADK tool compatibility - automatically appends hashtags to text

    Args:
        text: Tweet text (main content without hashtags)
        image_path: Path to generated image
        hashtags: Hashtag string (e.g., "#BuildInPublic #AIAgents" or "BuildInPublic, AIAgents")
        actually_post: Actually post or simulate

    Returns:
        JSON result from x_publish
    """
    # Append hashtags to text
    final_text = text.strip()

    if hashtags:
        hashtags_cleaned = hashtags.strip()

        # Handle comma-separated hashtags
        if ',' in hashtags_cleaned:
            tags = [tag.strip() for tag in hashtags_cleaned.split(',')]
            tags = ['#' + tag if not tag.startswith('#') else tag for tag in tags]
            hashtags_cleaned = ' '.join(tags)
        elif not hashtags_cleaned.startswith('#'):
            # Handle space-separated hashtags
            tags = hashtags_cleaned.split()
            tags = ['#' + tag if not tag.startswith('#') else tag for tag in tags]
            hashtags_cleaned = ' '.join(tags)

        # Append hashtags if not already in text
        if not any(tag in final_text for tag in hashtags_cleaned.split()):
            final_text = f"{final_text} {hashtags_cleaned}"

    print(f"[INFO] 최종 트윗 텍스트: {final_text}")

    return x_publish(
        text=final_text,
        image_path=image_path if image_path else None,
        actually_post=actually_post,
        require_approval=False
    )
