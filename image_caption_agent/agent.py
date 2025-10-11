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
    generate_image_concept,
    generate_twitter_image,
    generate_twitter_caption,
    generate_alt_text,
    calculate_safety_score,
)
from .schemas import ImageCaptionInput, ImageCaptionOutput, SafetyScore


# 오케스트레이터 에이전트 정의
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='image_caption_orchestrator',
    description="""Generates Twitter content: 3:4 image, caption (≤280 chars), ALT text, safety score.""",
    
    instruction="""Generate Twitter content: image (3:4 portrait), caption (≤280 chars), ALT text (80-120 chars), safety score.

Steps:
1. generate_image_concept(topic, tone)
2. generate_twitter_image(concept) - saves to artifacts, retry once if fails
3. generate_twitter_caption(topic, tone, locale, hashtags_allowed, concept)
4. generate_alt_text(concept, topic)
5. calculate_safety_score(caption, alt_text, topic, safety_bans)
6. load_artifacts() - to get final image for output

Complete all steps. Image is saved to artifacts (not in tool response to save tokens).""",
    
    tools=[
        generate_image_concept,
        generate_twitter_image,
        generate_twitter_caption,
        generate_alt_text,
        calculate_safety_score,
        load_artifacts,
    ],
)

# ADK 호환성을 위한 별칭
orchestrator_agent = root_agent


async def generate_image_caption_content(input_data: ImageCaptionInput) -> ImageCaptionOutput:
    """
    이미지와 캡션을 생성하는 메인 함수.
    
    Args:
        input_data: ImageCaptionInput 스키마 데이터
    
    Returns:
        ImageCaptionOutput: 생성된 이미지, 캡션, ALT 텍스트, 안전 점수
    """
    # 에이전트에 요청 전송
    request_message = f"""Generate Twitter content:
Topic: {input_data.topic}
Tone: {input_data.tone}
Locale: {input_data.locale}
Hashtags: {input_data.hashtagsAllowed}
Banned: {input_data.safetyBans or 'none'}"""
    
    response = await orchestrator_agent.run(request_message)
    
    # 응답 파싱 (실제 구현에서는 에이전트 응답을 파싱해야 함)
    # 여기서는 간단히 구조화된 출력을 가정
    return response

