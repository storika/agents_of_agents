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

from google.adk import Agent
from google.adk.tools import load_artifacts
from .tools import (
    generate_video_concept,
    generate_video_from_image,
    generate_video_from_text,
)
from .schemas import VideoGenerationInput, VideoGenerationOutput


# Video Generation Orchestrator Agent
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='video_generation_orchestrator',
    description="""Generates 8-second vertical videos (9:16) for social media from images or text prompts using Google Veo 3.""",

    instruction="""Generate short-form vertical videos (9:16 aspect ratio) optimized for Instagram Reels, TikTok, and YouTube Shorts.

**Workflow**:

**If given an image_path** (image-to-video):
1. generate_video_concept(image_concept, topic, tone) - Create motion/cinematography plan
2. generate_video_from_image(image_path, motion_prompt) - Generate 8s video with Veo 3
3. load_artifacts() - Verify video is saved

**If given only text prompt** (text-to-video):
1. generate_video_from_text(prompt, aspect_ratio="9:16") - Generate video directly from text
2. load_artifacts() - Verify video is saved

**Video Specifications**:
- Duration: 8 seconds
- Aspect Ratio: 9:16 (vertical)
- Resolution: 720p or 1080p
- Format: MP4
- Frame Rate: 24fps

**Motion Prompts Should Include**:
- Camera movements (zoom, pan, tilt, or static)
- Cinematography style (smooth, dynamic, cinematic)
- Visual mood (energetic, calm, mysterious, uplifting)
- Subject positioning (centered, rule of thirds)

**Generation Time**:
- Expect 11 seconds to 6 minutes for video generation
- Poll asynchronous operation until complete
- Videos are saved to artifacts/ directory

**Error Handling**:
- If generation fails, return error details
- If timeout occurs (>10 min), abort operation
- Retry once on transient errors

Complete all steps and return video_path when successful.""",

    tools=[
        generate_video_concept,
        generate_video_from_image,
        generate_video_from_text,
        load_artifacts,
    ],
)

# ADK compatibility alias
video_generation_orchestrator = root_agent


async def generate_video_content(input_data: VideoGenerationInput) -> VideoGenerationOutput:
    """
    비디오를 생성하는 메인 함수.

    Args:
        input_data: VideoGenerationInput 스키마 데이터

    Returns:
        VideoGenerationOutput: 생성된 비디오 경로 및 메타데이터
    """

    # Build request message
    request_message = f"""Generate video from image:
Image Path: {input_data.image_path}
Concept: {input_data.concept}
Topic: {input_data.topic}
Tone: {input_data.tone}
Duration: {input_data.duration}s
Aspect Ratio: {input_data.aspect_ratio}"""

    # Run agent
    response = await video_generation_orchestrator.run(request_message)

    # Parse response (in real implementation, parse agent response)
    # For now, return a structured output
    return VideoGenerationOutput(
        status="success",
        video_path="artifacts/generated_video.mp4",
        duration=input_data.duration,
        aspect_ratio=input_data.aspect_ratio,
        motion_prompt="Camera slowly zooms in on subject with smooth cinematic motion",
        generation_time=120.0
    )
