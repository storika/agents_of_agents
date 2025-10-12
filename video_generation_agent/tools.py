# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import Client, types
from google.adk.tools.tool_context import ToolContext

# Load environment variables
load_dotenv()

# Get API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client with API key
client = Client(api_key=GOOGLE_API_KEY)


async def generate_video_concept(
    image_concept: str,
    topic: str,
    tone: str,
    tool_context: ToolContext,
    include_audio: bool = True
) -> dict:
    """
    이미지 콘셉트를 바탕으로 비디오 모션/스토리 프롬프트를 생성합니다 (오디오 포함).

    Args:
        image_concept: 원본 이미지 콘셉트 설명
        topic: 콘텐츠 주제
        tone: 톤 (engaging, dramatic, calm, energetic)
        tool_context: 도구 컨텍스트
        include_audio: 오디오 프롬프트 포함 여부 (Veo 3는 기본적으로 오디오 생성)

    Returns:
        모션 프롬프트, 카메라 움직임, 시각 효과, 오디오 큐를 포함한 딕셔너리
    """

    audio_instruction = ""
    if include_audio:
        audio_instruction = """
5. AUDIO CUES (Veo 3 natively generates audio):
   - Dialogue: Use quotes for speech (e.g., "Check this out!")
   - Sound effects: Describe ambient sounds (e.g., soft music, whoosh, click)
   - Background: Mention environmental audio (e.g., gentle background music, upbeat track)

   Example: 'Upbeat electronic music plays. A voice says, "The future of AI is here!"'"""

    video_concept_prompt = f"""Create detailed 8-second video motion/story plan based on this image concept:

Image: {image_concept}
Topic: {topic}
Tone: {tone}

Generate a video prompt with:
1. Camera movement (slow zoom, pan, tilt, static)
2. Visual effects (fade in/out, lighting changes, color shifts)
3. Mood and energy (calm, energetic, mysterious, uplifting)
4. 8-second structure (0-3s: intro, 3-6s: main, 6-8s: outro){audio_instruction}

Requirements:
- Vertical 9:16 aspect ratio (Instagram Reels/TikTok/YouTube Shorts)
- Smooth, professional cinematography
- Keep subject centered and visible
- No abrupt cuts or jarring movements
- Suitable for social media (engaging, attention-grabbing)
- Audio should enhance the visual story (dialogue, sound effects, music)
- NO TEXT OVERLAYS - the video should be purely visual and audio

Output a single detailed prompt (3-4 sentences) describing the motion, cinematography, and audio. Do NOT include any text overlays or on-screen text."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=video_concept_prompt
        )

        motion_prompt = response.text.strip()

        return {
            'status': 'success',
            'motion_prompt': motion_prompt,
            'camera_movement': 'dynamic' if 'zoom' in motion_prompt.lower() or 'pan' in motion_prompt.lower() else 'static',
            'visual_effects': 'smooth' if 'smooth' in motion_prompt.lower() else 'dynamic',
            'mood': tone,
            'duration_plan': '8 seconds'
        }

    except Exception as e:
        return {
            'status': 'failed',
            'reason': f'Video concept generation error: {str(e)}'
        }


async def generate_video_from_image(
    image_path: str,
    motion_prompt: str,
    tool_context: ToolContext,
    aspect_ratio: str = "9:16",
    duration: int = 8
) -> dict:
    """
    이미지를 참조하여 Veo 3 API로 비디오를 생성합니다.

    Args:
        image_path: 참조 이미지 파일 경로
        motion_prompt: 모션/스토리 프롬프트
        tool_context: 도구 컨텍스트
        aspect_ratio: 비디오 비율 (9:16 for vertical, 16:9 for horizontal)
        duration: 비디오 길이 (초, 최대 8)

    Returns:
        비디오 파일 경로와 메타데이터를 포함한 딕셔너리
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
        operation = client.models.generate_videos(
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
            operation = client.operations.get(operation)

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
        video_bytes = client.files.download(file=generated_video.video)

        # Write video bytes to file
        with open(file_path, 'wb') as f:
            f.write(video_bytes)

        # Save to ADK artifacts (for UI/logging)
        with open(file_path, 'rb') as f:
            video_bytes = f.read()

        await tool_context.save_artifact(
            filename,
            types.Part.from_bytes(data=video_bytes, mime_type='video/mp4'),
        )

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


async def generate_video_from_text(
    prompt: str,
    tool_context: ToolContext,
    aspect_ratio: str = "9:16",
    duration: int = 8
) -> dict:
    """
    텍스트 프롬프트만으로 비디오를 생성합니다 (이미지 참조 없이).

    Args:
        prompt: 비디오 생성 프롬프트
        tool_context: 도구 컨텍스트
        aspect_ratio: 비디오 비율 (9:16 for vertical, 16:9 for horizontal)
        duration: 비디오 길이 (초, 최대 8)

    Returns:
        비디오 파일 경로와 메타데이터를 포함한 딕셔너리
    """

    start_time = time.time()

    try:
        # Enhance prompt for vertical video
        enhanced_prompt = f"{prompt}. Vertical 9:16 format optimized for social media. Professional quality, smooth cinematography."

        print(f"[INFO] Starting text-to-video generation with Veo 3...")
        print(f"[INFO] Prompt: {enhanced_prompt[:100]}...")

        # Generate video using Veo 3
        operation = client.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt=enhanced_prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
            )
        )

        operation_name = operation.name
        print(f"[INFO] Operation started: {operation_name}")
        print(f"[INFO] Polling for completion (this may take 11 seconds to 6 minutes)...")

        # Poll until operation is done
        poll_count = 0
        max_polls = 60

        while not operation.done:
            poll_count += 1
            elapsed = time.time() - start_time

            if poll_count % 6 == 0:
                print(f"[INFO] Still generating... (elapsed: {elapsed:.0f}s)")

            if poll_count >= max_polls:
                return {
                    'status': 'failed',
                    'reason': f'Video generation timed out after {elapsed:.0f}s'
                }

            time.sleep(10)
            operation = client.operations.get(operation)

        generation_time = time.time() - start_time
        print(f"[INFO] Video generation completed in {generation_time:.1f}s")

        # Get the generated video
        if not operation.response or not operation.response.generated_videos:
            return {
                'status': 'failed',
                'reason': 'No video generated in response'
            }

        generated_video = operation.response.generated_videos[0]

        # Save video
        artifacts_dir = 'artifacts'
        os.makedirs(artifacts_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'generated_video_{timestamp}.mp4'
        file_path = os.path.join(artifacts_dir, filename)

        print(f"[INFO] Downloading video to: {file_path}")
        video_bytes = client.files.download(file=generated_video.video)

        # Write video bytes to file
        with open(file_path, 'wb') as f:
            f.write(video_bytes)

        # Save to ADK artifacts
        with open(file_path, 'rb') as f:
            video_bytes = f.read()

        await tool_context.save_artifact(
            filename,
            types.Part.from_bytes(data=video_bytes, mime_type='video/mp4'),
        )

        print(f"[INFO] Video saved successfully: {file_path}")

        return {
            'status': 'success',
            'video_path': file_path,
            'filename': filename,
            'duration': duration,
            'aspect_ratio': aspect_ratio,
            'prompt': prompt,
            'generation_time': generation_time,
            'detail': f'Video saved to {file_path} ({aspect_ratio}, {duration}s)'
        }

    except Exception as e:
        generation_time = time.time() - start_time
        error_msg = f'Video generation error after {generation_time:.1f}s: {str(e)}'
        print(f"[ERROR] {error_msg}")

        return {
            'status': 'failed',
            'reason': error_msg,
            'generation_time': generation_time
        }
