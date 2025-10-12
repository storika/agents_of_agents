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
from google import genai
from google.genai import Client, types

# Twitter API URLs
TWITTER_API_V2_URL = "https://api.twitter.com/2/tweets"
TWITTER_MEDIA_UPLOAD_V2_URL = "https://upload.twitter.com/2/media/upload.json"
TWITTER_MEDIA_UPLOAD_V1_URL = "https://upload.twitter.com/1.1/media/upload.json"

# Initialize Gemini clients for image/video generation
gemini_text_client = Client()
gemini_image_client = genai.Client()


@weave.op()
def upload_video_chunked(oauth1_creds: dict, video_path: str) -> Optional[str]:
    """
    Upload video using Twitter's chunked upload API (required for videos)
    https://developer.twitter.com/en/docs/media/upload-media/uploading-media/chunked-media-upload

    Args:
        oauth1_creds: OAuth 1.0a credentials
        video_path: Path to video file

    Returns:
        media_id_string on success, None on failure
    """
    if not all(oauth1_creds.values()):
        print(f"[ERROR] OAuth 1.0a credentials required for video upload")
        return None

    try:
        from requests_oauthlib import OAuth1
    except ImportError:
        print(f"[ERROR] requests-oauthlib required: pip install requests-oauthlib")
        return None

    auth = OAuth1(
        oauth1_creds["consumer_key"],
        oauth1_creds["consumer_secret"],
        oauth1_creds["access_token"],
        oauth1_creds["access_secret"],
        signature_type='auth_header'
    )

    # Get file size
    video_size = os.path.getsize(video_path)
    print(f"[INFO] Video size: {video_size / (1024*1024):.2f} MB")

    try:
        # Step 1: INIT
        print(f"[INFO] Step 1: INIT chunked upload")
        init_data = {
            "command": "INIT",
            "media_type": "video/mp4",
            "total_bytes": video_size,
            "media_category": "tweet_video"
        }
        response = requests.post(TWITTER_MEDIA_UPLOAD_V1_URL, auth=auth, data=init_data, timeout=30)

        if response.status_code != 202:
            print(f"[ERROR] INIT failed: {response.status_code} - {response.text}")
            return None

        media_id = response.json().get("media_id_string")
        print(f"[INFO] Media ID: {media_id}")

        # Step 2: APPEND (upload in chunks)
        print(f"[INFO] Step 2: APPEND chunks")
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        segment_index = 0

        with open(video_path, 'rb') as video_file:
            while True:
                chunk = video_file.read(chunk_size)
                if not chunk:
                    break

                append_data = {
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": segment_index
                }
                files = {"media": chunk}

                response = requests.post(TWITTER_MEDIA_UPLOAD_V1_URL, auth=auth, data=append_data, files=files, timeout=60)

                if response.status_code not in [200, 201, 204]:
                    print(f"[ERROR] APPEND failed at segment {segment_index}: {response.status_code}")
                    return None

                segment_index += 1
                print(f"[INFO] Uploaded segment {segment_index}")

        # Step 3: FINALIZE
        print(f"[INFO] Step 3: FINALIZE upload")
        finalize_data = {
            "command": "FINALIZE",
            "media_id": media_id
        }
        response = requests.post(TWITTER_MEDIA_UPLOAD_V1_URL, auth=auth, data=finalize_data, timeout=30)

        if response.status_code not in [200, 201]:
            print(f"[ERROR] FINALIZE failed: {response.status_code} - {response.text}")
            return None

        result = response.json()
        processing_info = result.get("processing_info")

        # Step 4: STATUS check (if processing required)
        if processing_info:
            state = processing_info.get("state")
            print(f"[INFO] Processing state: {state}")

            while state in ["pending", "in_progress"]:
                check_after_secs = processing_info.get("check_after_secs", 1)
                print(f"[INFO] Waiting {check_after_secs}s for processing...")
                time.sleep(check_after_secs)

                status_params = {
                    "command": "STATUS",
                    "media_id": media_id
                }
                response = requests.get(TWITTER_MEDIA_UPLOAD_V1_URL, auth=auth, params=status_params, timeout=30)

                if response.status_code != 200:
                    print(f"[ERROR] STATUS check failed: {response.status_code}")
                    return None

                processing_info = response.json().get("processing_info", {})
                state = processing_info.get("state")
                print(f"[INFO] Processing state: {state}")

            if state == "failed":
                error = processing_info.get("error", {})
                print(f"[ERROR] Video processing failed: {error}")
                return None

        print(f"[INFO] ✅ Video upload successful: {media_id}")
        return media_id

    except Exception as e:
        print(f"[ERROR] Video upload error: {e}")
        import traceback
        traceback.print_exc()
        return None


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
    Supports both images and videos

    Args:
        image_path: Path to image or video file

    Returns:
        media_id_string on success, None on failure
    """
    load_dotenv()

    if not os.path.exists(image_path):
        print(f"[ERROR] 미디어 파일을 찾을 수 없습니다: {image_path}")
        return None

    # Check if it's a video file
    is_video = image_path.lower().endswith(('.mp4', '.mov', '.avi', '.webm'))

    if is_video:
        print(f"[INFO] 비디오 파일 감지: {image_path}")
        # Videos must use OAuth 1.0a with chunked upload
        oauth1_creds = {
            "consumer_key": os.getenv("TW_CONSUMER_KEY"),
            "consumer_secret": os.getenv("TW_CONSUMER_SECRET"),
            "access_token": os.getenv("TW_ACCESS_TOKEN"),
            "access_secret": os.getenv("TW_ACCESS_TOKEN_SECRET"),
        }
        return upload_video_chunked(oauth1_creds, image_path)

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

            # Log rate limit headers for debugging
            rate_limit_headers = {
                'limit': response.headers.get('x-rate-limit-limit'),
                'remaining': response.headers.get('x-rate-limit-remaining'),
                'reset': response.headers.get('x-rate-limit-reset'),
                'app_24h_limit': response.headers.get('x-app-limit-24hour-limit'),
                'app_24h_remaining': response.headers.get('x-app-limit-24hour-remaining'),
                'app_24h_reset': response.headers.get('x-app-limit-24hour-reset'),
                'user_24h_limit': response.headers.get('x-user-limit-24hour-limit'),
                'user_24h_remaining': response.headers.get('x-user-limit-24hour-remaining'),
                'user_24h_reset': response.headers.get('x-user-limit-24hour-reset')
            }

            if rate_limit_headers['remaining'] is not None:
                reset_time = int(rate_limit_headers['reset']) if rate_limit_headers['reset'] else 0
                from datetime import datetime
                reset_dt = datetime.fromtimestamp(reset_time) if reset_time > 0 else None
                reset_str = reset_dt.strftime('%Y-%m-%d %H:%M:%S') if reset_dt else 'unknown'

                print(f"[RATE_LIMIT] General: {rate_limit_headers['remaining']}/{rate_limit_headers['limit']} (resets at {reset_str})")

            # Log 24-hour limits
            if rate_limit_headers['app_24h_remaining'] is not None:
                app_reset_time = int(rate_limit_headers['app_24h_reset']) if rate_limit_headers['app_24h_reset'] else 0
                from datetime import datetime
                app_reset_dt = datetime.fromtimestamp(app_reset_time) if app_reset_time > 0 else None
                app_reset_str = app_reset_dt.strftime('%Y-%m-%d %H:%M:%S') if app_reset_dt else 'unknown'

                print(f"[RATE_LIMIT] App 24h: {rate_limit_headers['app_24h_remaining']}/{rate_limit_headers['app_24h_limit']} (resets at {app_reset_str})")
                print(f"[RATE_LIMIT] User 24h: {rate_limit_headers['user_24h_remaining']}/{rate_limit_headers['user_24h_limit']}")

            # Debug: Show actual HTTP status
            print(f"[DEBUG] HTTP Status: {response.status_code}")

            if response.status_code == 201:
                data = response.json()
                return data.get("data", {})
            elif response.status_code == 403:
                print(f"[ERROR] 403 Forbidden - X API 권한 문제")
                print(f"[ERROR] Response: {response.text}")
                return None
            elif response.status_code == 429:
                # Determine which rate limit was hit
                from datetime import datetime
                import time as time_module

                app_24h_remaining = rate_limit_headers.get('app_24h_remaining')
                user_24h_remaining = rate_limit_headers.get('user_24h_remaining')

                if app_24h_remaining == '0' or user_24h_remaining == '0':
                    # Hit the 24-hour limit
                    reset_timestamp = rate_limit_headers.get('app_24h_reset')
                    if reset_timestamp:
                        reset_dt = datetime.fromtimestamp(int(reset_timestamp))
                        reset_str = reset_dt.strftime('%Y-%m-%d %H:%M:%S')
                        wait_seconds = int(reset_timestamp) - int(time_module.time())
                        wait_hours = wait_seconds / 3600

                        print(f"\n{'='*60}")
                        print(f"[ERROR] ⚠️  24-HOUR RATE LIMIT EXCEEDED!")
                        print(f"{'='*60}")
                        print(f"[ERROR] Your app has a limit of {rate_limit_headers['app_24h_limit']} tweets per 24 hours")
                        print(f"[ERROR] App remaining: {rate_limit_headers['app_24h_remaining']}/{rate_limit_headers['app_24h_limit']}")
                        print(f"[ERROR] User remaining: {rate_limit_headers['user_24h_remaining']}/{rate_limit_headers['user_24h_limit']}")
                        print(f"[ERROR] Resets at: {reset_str} (in {wait_hours:.1f} hours)")
                        print(f"[INFO] This is separate from the general API rate limit (1.08M requests)")
                        print(f"\n[INFO] 📋 MANUAL POSTING INFO:")
                        print(f"[INFO] Tweet text: {payload.get('text', 'N/A')}")
                        if payload.get('media', {}).get('media_ids'):
                            print(f"[INFO] Media IDs: {payload['media']['media_ids']}")
                        print(f"{'='*60}\n")
                    else:
                        print(f"[ERROR] 24-hour rate limit exceeded (no reset time available)")
                else:
                    # Hit the general rate limit
                    reset_timestamp = rate_limit_headers.get('reset')
                    if reset_timestamp:
                        reset_dt = datetime.fromtimestamp(int(reset_timestamp))
                        reset_str = reset_dt.strftime('%Y-%m-%d %H:%M:%S')
                        wait_seconds = int(reset_timestamp) - int(time_module.time())
                        print(f"[ERROR] General rate limit exceeded!")
                        print(f"[ERROR] Limit: {rate_limit_headers['limit']} requests")
                        print(f"[ERROR] Remaining: {rate_limit_headers['remaining']}")
                        print(f"[ERROR] Resets at: {reset_str} (in {wait_seconds}s)")
                    else:
                        print(f"[ERROR] Rate limit exceeded (no reset time available)")

                if attempt == max_retries:
                    return None
                print(f"[WARN] Rate limited. Retry #{attempt} in {delay}s")
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
            # Failed to post (likely rate limited)
            print(f"\n{'='*60}")
            print(f"[INFO] 📋 MANUAL POSTING INFORMATION")
            print(f"{'='*60}")
            print(f"[INFO] Tweet text: {text}")
            if image_path:
                print(f"[INFO] Image path: {image_path}")
            if media_keys:
                print(f"[INFO] Media ID (already uploaded): {media_keys[0]}")
            print(f"[INFO] You can manually post this content on Twitter/X")
            print(f"{'='*60}\n")

            result = {
                "status": "failed",
                "post_id": f"failed_{datetime.now().timestamp()}",
                "text": text,
                "image_path": image_path,
                "media_id": media_keys[0] if media_keys else None,
                "message": "⚠️ 포스팅 실패 (Rate Limit). 위의 정보로 수동 포스팅 가능합니다."
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
        hashtags: Hashtag string (e.g., "#Trending #News" or "Trending, News")
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


# ===== IMAGE GENERATION TOOLS =====

@weave.op()
def generate_twitter_image(concept: str, retry: bool = False) -> dict:
    """
    Generate a 3:4 portrait image for Twitter based on a concept.

    Args:
        concept: Image concept description
        retry: If True, simplify the prompt for retry

    Returns:
        Dictionary with status, file_path, and other metadata
    """
    # Prepare prompt
    if retry:
        prompt = f"Simple, clean image: {concept[:200]}"
    else:
        prompt = concept

    # Add aspect ratio specification
    prompt = f"{prompt}. Aspect ratio: 3:4 portrait, high quality, professional, suitable for social media."

    try:
        response = gemini_image_client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[prompt],
        )

        # Extract image data from response
        image_bytes = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_bytes = part.inline_data.data
                break

        if image_bytes is None:
            return {
                'status': 'failed',
                'reason': 'No image generated in response'
            }

        # Create artifacts directory
        artifacts_dir = 'artifacts'
        os.makedirs(artifacts_dir, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'generated_image_{timestamp}.png'
        file_path = os.path.join(artifacts_dir, filename)

        # Save to file system (for X API upload)
        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        print(f"[INFO] Image saved to: {file_path}")

        return {
            'status': 'success',
            'detail': f'Image saved to {file_path} (3:4 portrait)',
            'filename': filename,
            'file_path': file_path,
            'concept_used': concept
        }

    except Exception as e:
        return {
            'status': 'failed',
            'reason': f'Image generation error: {str(e)}'
        }


# ===== VIDEO GENERATION TOOLS =====

@weave.op()
def generate_video_from_image(
    image_path: str,
    motion_prompt: str,
    aspect_ratio: str = "9:16",
    duration: int = 8
) -> dict:
    """
    Generate video from image using Veo 3 API.

    Args:
        image_path: Path to reference image file
        motion_prompt: Motion/story prompt for the video
        aspect_ratio: Video aspect ratio (9:16 for vertical, 16:9 for horizontal)
        duration: Video length in seconds (max 8)

    Returns:
        Dictionary with status, video_path, and metadata
    """
    start_time = time.time()

    try:
        # Check if image file exists
        if not os.path.exists(image_path):
            return {
                'status': 'failed',
                'reason': f'Image file not found: {image_path}'
            }

        print(f"[INFO] Loading reference image: {image_path}")

        # Read image file as bytes
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        print(f"[INFO] Image loaded ({len(image_bytes)} bytes)")

        # Enhance prompt for vertical video with audio
        enhanced_prompt = f"{motion_prompt}. Vertical 9:16 format optimized for social media stories and reels. Professional cinematography with smooth camera movements and audio."

        print(f"[INFO] Starting video generation with Veo 3...")
        print(f"[INFO] Prompt: {enhanced_prompt[:100]}...")
        print(f"[INFO] Aspect ratio: {aspect_ratio}, Duration: {duration}s")

        # Generate video using Veo 3 with image bytes
        operation = gemini_text_client.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt=enhanced_prompt,
            image={
                "imageBytes": image_bytes,
                "mimeType": "image/png"
            },
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
            )
        )

        operation_name = operation.name
        print(f"[INFO] Operation started: {operation_name}")
        print(f"[INFO] Polling for completion (this may take 11 seconds to 6 minutes)...")

        # Poll until operation is done
        poll_count = 0
        max_polls = 60  # 10 minutes max (60 * 10s = 600s)

        while not operation.done:
            poll_count += 1
            elapsed = time.time() - start_time

            if poll_count % 6 == 0:  # Log every minute
                print(f"[INFO] Still generating... (elapsed: {elapsed:.0f}s)")

            if poll_count >= max_polls:
                return {
                    'status': 'failed',
                    'reason': f'Video generation timed out after {elapsed:.0f}s'
                }

            time.sleep(10)  # Poll every 10 seconds
            operation = gemini_text_client.operations.get(operation)

        generation_time = time.time() - start_time
        print(f"[INFO] Video generation completed in {generation_time:.1f}s")

        # Get the generated video
        if not operation.response or not operation.response.generated_videos:
            return {
                'status': 'failed',
                'reason': 'No video generated in response'
            }

        generated_video = operation.response.generated_videos[0]

        # Create artifacts directory
        artifacts_dir = 'artifacts'
        os.makedirs(artifacts_dir, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'generated_video_{timestamp}.mp4'
        file_path = os.path.join(artifacts_dir, filename)

        # Download video
        print(f"[INFO] Downloading video to: {file_path}")
        video_bytes = gemini_text_client.files.download(file=generated_video.video)

        # Write video bytes to file
        with open(file_path, 'wb') as f:
            f.write(video_bytes)

        print(f"[INFO] Video saved successfully: {file_path}")

        return {
            'status': 'success',
            'video_path': file_path,
            'filename': filename,
            'duration': duration,
            'aspect_ratio': aspect_ratio,
            'motion_prompt': motion_prompt,
            'generation_time': generation_time,
            'detail': f'Video saved to {file_path} ({aspect_ratio}, {duration}s)'
        }

    except Exception as e:
        import traceback
        generation_time = time.time() - start_time
        error_msg = f'Video generation error after {generation_time:.1f}s: {str(e)}'
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback:")
        traceback.print_exc()

        return {
            'status': 'failed',
            'reason': error_msg,
            'generation_time': generation_time
        }
