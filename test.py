import argparse
import json
import os
import sys
import time
from typing import List, Optional

import requests
from dotenv import load_dotenv

# OAuth 2.0 개발 환경에서 localhost HTTP 허용
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

STATE_DEFAULT_PATH = ".tweet_state.json"
TWITTER_API_V2_URL = "https://api.twitter.com/2/tweets"
# V2 Media Upload API 시도
TWITTER_MEDIA_UPLOAD_V2_URL = "https://upload.twitter.com/2/media/upload.json"
# V1.1 fallback
TWITTER_MEDIA_UPLOAD_V1_URL = "https://upload.twitter.com/1.1/media/upload.json"

def load_env():
    load_dotenv()
    # OAuth 2.0 (트윗 생성용) + OAuth 1.0a (미디어 업로드용)
    oauth2_token = os.getenv("TW_OAUTH2_ACCESS_TOKEN")
    
    # OAuth 1.0a credentials (미디어 업로드에 필요)
    consumer_key = os.getenv("TW_CONSUMER_KEY")
    consumer_secret = os.getenv("TW_CONSUMER_SECRET")
    access_token = os.getenv("TW_ACCESS_TOKEN")
    access_secret = os.getenv("TW_ACCESS_SECRET")
    
    if not oauth2_token:
        print(f"[ERROR] TW_OAUTH2_ACCESS_TOKEN이 .env 파일에 없습니다.", file=sys.stderr)
        print("\nOAuth 2.0 설정 방법:", file=sys.stderr)
        print("1. .env 파일에 다음을 추가하세요:", file=sys.stderr)
        print("   TW_CLIENT_ID=your_client_id", file=sys.stderr)
        print("   TW_CLIENT_SECRET=your_client_secret", file=sys.stderr)
        print("2. oauth2_setup.py를 실행하여 Access Token 발급:", file=sys.stderr)
        print("   python oauth2_setup.py", file=sys.stderr)
        sys.exit(1)
    
    return {
        "oauth2_token": oauth2_token,
        "oauth1_credentials": {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": access_token,
            "access_secret": access_secret
        }
    }

def read_messages_from_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines()]
    # drop empty lines
    return [ln for ln in lines if ln]

def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return {"next_index": 0}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"next_index": 0}

def save_state(path: str, state: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def upload_media_v2(oauth2_token: str, image_path: str) -> Optional[str]:
    """미디어 업로드 V2 시도 (OAuth 2.0 Bearer Token)"""
    print(f"[INFO] V2 API 시도 (OAuth 2.0): {image_path}")
    
    headers = {
        "Authorization": f"Bearer {oauth2_token}",
    }
    
    try:
        with open(image_path, 'rb') as f:
            files = {'media': f}
            
            response = requests.post(
                TWITTER_MEDIA_UPLOAD_V2_URL,
                headers=headers,
                files=files,
                timeout=30
            )
        
        print(f"[DEBUG] V2 Upload status: {response.status_code}")
        print(f"[DEBUG] V2 Upload response: {response.text[:200]}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            # V2는 media_id_string 반환
            media_id = result.get("media_id_string") or result.get("data", {}).get("media_id_string")
            if media_id:
                print(f"[OK] V2 미디어 업로드 성공: {media_id}")
                return media_id
        
        print(f"[WARN] V2 API 실패 (status={response.status_code}), V1.1로 fallback")
        return None
    except Exception as e:
        print(f"[WARN] V2 API 에러: {e}, V1.1로 fallback")
        return None


def upload_media_v1(oauth1_creds: dict, image_path: str) -> Optional[str]:
    """미디어 업로드 V1.1 (OAuth 1.0a)"""
    print(f"[INFO] V1.1 API 시도 (OAuth 1.0a): {image_path}")
    
    # OAuth 1.0a 필요 여부 확인
    print(f"[DEBUG] OAuth 1.0a credentials 상태:")
    print(f"  consumer_key: {'✓' if oauth1_creds.get('consumer_key') else '✗ 없음'}")
    print(f"  consumer_secret: {'✓' if oauth1_creds.get('consumer_secret') else '✗ 없음'}")
    print(f"  access_token: {'✓' if oauth1_creds.get('access_token') else '✗ 없음'}")
    print(f"  access_secret: {'✓' if oauth1_creds.get('access_secret') else '✗ 없음'}")
    
    if not all(oauth1_creds.values()):
        print(f"[ERROR] OAuth 1.0a credentials 필요:", file=sys.stderr)
        print("  .env 파일에 다음 추가:", file=sys.stderr)
        print("  TW_CONSUMER_KEY=your_api_key", file=sys.stderr)
        print("  TW_CONSUMER_SECRET=your_api_secret", file=sys.stderr)
        print("  TW_ACCESS_TOKEN=your_access_token", file=sys.stderr)
        print("  TW_ACCESS_SECRET=your_access_secret", file=sys.stderr)
        print("\n  ⚠️ 주의: OAuth 2.0 토큰이 아닌 OAuth 1.0a 토큰이어야 합니다!", file=sys.stderr)
        return None
    
    # requests-oauthlib 사용
    try:
        from requests_oauthlib import OAuth1
    except ImportError:
        print(f"[ERROR] requests-oauthlib 필요: pip install requests-oauthlib", file=sys.stderr)
        return None
    
    print(f"[DEBUG] OAuth 1.0a 서명 생성 중...")
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
            
            response = requests.post(
                TWITTER_MEDIA_UPLOAD_V1_URL,
                auth=auth,
                files=files,
                timeout=30
            )
            
        print(f"[DEBUG] V1.1 Upload status: {response.status_code}")
        print(f"[DEBUG] V1.1 Upload response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            media_id = result.get("media_id_string")
            if media_id:
                print(f"[OK] V1.1 미디어 업로드 성공: {media_id}")
                return media_id
        elif response.status_code == 403:
            print(f"[ERROR] 403 Forbidden - 가능한 원인:", file=sys.stderr)
            print("  1. App Permissions가 'Read and Write'가 아님", file=sys.stderr)
            print("  2. Access Token이 권한 변경 전에 생성됨 (재생성 필요)", file=sys.stderr)
            print("  3. OAuth 2.0 Access Token을 OAuth 1.0a로 사용 중", file=sys.stderr)
            print("\n  해결 방법:", file=sys.stderr)
            print("  - X Developer Portal → Settings → App permissions → Read and Write", file=sys.stderr)
            print("  - Keys and tokens → Access Token and Secret 재생성", file=sys.stderr)
            print("  - .env의 TW_ACCESS_TOKEN, TW_ACCESS_SECRET 업데이트", file=sys.stderr)
            return None
        
        print(f"[ERROR] V1.1 API 실패: {response.status_code}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[ERROR] V1.1 Upload error: {e}", file=sys.stderr)
        return None


def upload_media(oauth2_token: str, oauth1_creds: dict, image_path: str) -> Optional[str]:
    """미디어 업로드 (V2 시도 → V1.1 fallback)"""
    if not os.path.exists(image_path):
        print(f"[ERROR] 이미지 파일을 찾을 수 없습니다: {image_path}", file=sys.stderr)
        return None
    
    # 1. V2 API 먼저 시도 (OAuth 2.0)
    media_id = upload_media_v2(oauth2_token, image_path)
    if media_id:
        return media_id
    
    # 2. V1.1 API로 fallback (OAuth 1.0a)
    print("[INFO] V2 실패, V1.1 API 사용")
    media_id = upload_media_v1(oauth1_creds, image_path)
    return media_id

def safe_create_tweet(access_token: str, text: str, media_ids: Optional[List[str]] = None, max_retries: int = 3) -> Optional[dict]:
    """Post a tweet using OAuth 2.0 with basic retry on transient errors (e.g., 429/5xx)."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {"text": text}
    
    # 미디어가 있으면 추가
    if media_ids:
        payload["media"] = {"media_ids": media_ids}
    
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
                # 403 오류는 권한 문제이므로 재시도해도 해결되지 않습니다
                print(f"\n[ERROR] 403 Forbidden - 권한 문제가 발생했습니다.", file=sys.stderr)
                print("해결 방법:", file=sys.stderr)
                print("1. https://developer.twitter.com/en/portal/dashboard 접속", file=sys.stderr)
                print("2. 앱 선택 → Settings → User authentication settings", file=sys.stderr)
                print("3. 'App permissions'를 'Read and Write' 또는 'Read and Write and Direct Messages'로 변경", file=sys.stderr)
                print("4. oauth2_setup.py를 다시 실행하여 새 토큰 발급\n", file=sys.stderr)
                print(f"응답: {response.text}\n", file=sys.stderr)
                raise Exception(f"403 Forbidden: {response.text}")
            elif response.status_code == 429:
                # Rate limit
                if attempt == max_retries:
                    raise Exception(f"429 Too Many Requests: {response.text}")
                print(f"[WARN] Rate limited. Retry in {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                # 다른 오류
                if attempt == max_retries:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                print(f"[WARN] HTTP {response.status_code}: {response.text}. Retry in {delay}s (attempt {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                raise
            print(f"[WARN] Request error: {e}. Retry in {delay}s (attempt {attempt}/{max_retries})")
            time.sleep(delay)
            delay *= 2
    
    return None

def post_once(oauth2_token: str, oauth1_creds: dict, text: str, image_path: Optional[str] = None):
    if not text or not text.strip():
        print("[ERROR] Empty text.", file=sys.stderr)
        sys.exit(2)
    
    media_ids = None
    if image_path:
        # V2 시도 → V1.1 fallback
        media_id = upload_media(oauth2_token, oauth1_creds, image_path)
        if media_id:
            media_ids = [media_id]
        else:
            print("[ERROR] 이미지 업로드 실패. 포스팅을 중단합니다.", file=sys.stderr)
            sys.exit(1)
    
    res = safe_create_tweet(oauth2_token, text.strip(), media_ids=media_ids)
    print(f"[OK] Tweeted: {text}\n[id={res.get('id') if res else 'unknown'}]")
    if media_ids:
        print(f"[OK] With image: {image_path}")

def post_next_from_list(access_token: str, messages: List[str], state_path: str, wrap: bool):
    if not messages:
        print("[ERROR] No messages to post.", file=sys.stderr)
        sys.exit(2)

    state = load_state(state_path)
    idx = state.get("next_index", 0)

    if idx >= len(messages):
        if not wrap:
            print("[DONE] No more messages (and wrap=False).")
            return
        idx = 0

    text = messages[idx]
    res = safe_create_tweet(access_token, text)
    print(f"[OK] Tweeted (#{idx+1}/{len(messages)}): {text}\n[id={res.get('id') if res else 'unknown'}]")

    state["next_index"] = idx + 1
    save_state(state_path, state)

def main():
    parser = argparse.ArgumentParser(description="Post tweets with OAuth 2.0 user context (X/Twitter).")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", type=str, help="Post a single tweet (one-off).")
    g.add_argument("--messages", type=str, help="Path to a text file (one tweet per line).")

    parser.add_argument("--image", type=str, help="Path to image file to attach (only with --text).")
    parser.add_argument("--state", type=str, default=STATE_DEFAULT_PATH, help="Path to state file (for --messages).")
    parser.add_argument("--wrap", action="store_true", help="Loop back to first message after reaching the end.")
    args = parser.parse_args()

    creds = load_env()

    if args.text:
        post_once(creds["oauth2_token"], creds["oauth1_credentials"], args.text, image_path=args.image)
    else:
        if args.image:
            print("[WARN] --image is only supported with --text, ignoring.", file=sys.stderr)
        msgs = read_messages_from_file(args.messages)
        post_next_from_list(creds["oauth2_token"], msgs, args.state, args.wrap)

if __name__ == "__main__":
    main()
