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

import base64
import re
from typing import Optional
from google.genai import Client
from google.genai import types
from google.adk.tools.tool_context import ToolContext

# Vertex AI 클라이언트 초기화
client = Client()


async def generate_image_concept(
    topic: str,
    tone: str,
    tool_context: ToolContext
) -> dict:
    """
    주제와 톤을 바탕으로 이미지 콘셉트를 생성합니다.
    
    Args:
        topic: 이미지 주제
        tone: 톤 (friendly, witty, informative, minimal)
        tool_context: 도구 컨텍스트
    
    Returns:
        콘셉트 설명, 비주얼 태그, 네거티브 태그를 포함한 딕셔너리
    """
    concept_prompt = f"""Create 3:4 portrait image concept for topic '{topic}' with '{tone}' tone.
Output:
1. Concept: 1-2 sentences (subject, background, lighting, mood)
2. Visual tags: 5-10 (e.g. close-up, soft light, vibrant colors)
3. Negative tags: text, logo, watermark, low quality, distorted
Keep it Twitter-friendly, no brands/text/sensitive content."""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=concept_prompt
    )
    
    concept_text = response.text
    return {
        'status': 'success',
        'concept': concept_text
    }


async def generate_twitter_image(
    concept: str,
    tool_context: ToolContext,
    retry: bool = False
) -> dict:
    """
    콘셉트를 바탕으로 3:4 비율의 세로형 이미지를 생성합니다.
    
    Args:
        concept: 이미지 콘셉트 설명
        tool_context: 도구 컨텍스트
        retry: 재시도 여부 (True면 프롬프트를 축약)
    
    Returns:
        Base64로 인코딩된 이미지 또는 실패 메시지
    """
    # 프롬프트 준비
    if retry:
        # 재시도 시 콘셉트를 더 단순하게
        prompt = f"Simple, clean image: {concept[:200]}"
    else:
        prompt = concept
    
    # 3:4 세로형 비율 명시 추가
    prompt = f"{prompt}. Aspect ratio: 3:4 portrait, high quality, professional, suitable for social media."
    
    try:
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config={
                'number_of_images': 1,
                'aspect_ratio': '3:4',  # 3:4 세로형 비율
            },
        )
        
        if not response.generated_images:
            return {
                'status': 'failed',
                'reason': 'No images generated'
            }
        
        # 이미지를 artifact에 저장 (토큰 절약)
        image_bytes = response.generated_images[0].image.image_bytes
        await tool_context.save_artifact(
            'twitter_image.png',
            types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
        )
        
        return {
            'status': 'success',
            'detail': 'Image saved to artifacts as twitter_image.png (3:4 portrait, 896×1280)',
            'filename': 'twitter_image.png'
        }
    
    except Exception as e:
        return {
            'status': 'failed',
            'reason': f'Image generation error: {str(e)}'
        }


async def generate_twitter_caption(
    topic: str,
    tone: str,
    locale: str,
    hashtags_allowed: int,
    image_concept: str,
    tool_context: ToolContext
) -> dict:
    """
    트위터용 캡션을 생성합니다 (≤280자, 이모지 허용).
    
    Args:
        topic: 주제
        tone: 톤
        locale: 언어 코드
        hashtags_allowed: 허용되는 해시태그 개수
        image_concept: 생성된 이미지 콘셉트
        tool_context: 도구 컨텍스트
    
    Returns:
        생성된 캡션 (≤280자)
    """
    caption_prompt = f"""Write Twitter caption for '{topic}' in {locale} language.
Tone: {tone} | Max: 280 chars | Hashtags: max {hashtags_allowed} | Emojis: 1-3

Structure: Hook (question/stat/contrast) → Value/emotion → Call-to-action
Avoid: clickbait, hate, medical/financial claims, excessive hashtags/emojis

Image concept: {image_concept}

Output caption only."""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=caption_prompt
    )
    
    caption = response.text.strip()
    
    # 길이 확인 및 조정
    if len(caption) > 280:
        caption = caption[:277] + "..."
    
    return {
        'status': 'success',
        'caption': caption,
        'length': len(caption)
    }


async def generate_alt_text(
    image_concept: str,
    topic: str,
    tool_context: ToolContext
) -> dict:
    """
    이미지에 대한 ALT 텍스트를 생성합니다 (80-120자).
    
    Args:
        image_concept: 이미지 콘셉트 설명
        topic: 주제
        tool_context: 도구 컨텍스트
    
    Returns:
        생성된 ALT 텍스트 (80-120자)
    """
    alt_prompt = f"""Write ALT text for image about '{topic}'.
Concept: {image_concept}

Requirements: 80-120 chars, factual description (scene, objects, colors, composition)
Output ALT text only."""
    
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=alt_prompt
    )
    
    alt_text = response.text.strip()
    
    # 길이 조정
    if len(alt_text) < 80:
        alt_text = alt_text + " " * (80 - len(alt_text))  # 최소 길이 확보
    elif len(alt_text) > 120:
        alt_text = alt_text[:117] + "..."
    
    return {
        'status': 'success',
        'altText': alt_text,
        'length': len(alt_text)
    }


async def calculate_safety_score(
    caption: str,
    alt_text: str,
    topic: str,
    safety_bans: Optional[list[str]],
    tool_context: ToolContext
) -> dict:
    """
    캡션과 ALT 텍스트의 안전 점수를 계산합니다 (0-1).
    
    Args:
        caption: 생성된 캡션
        alt_text: 생성된 ALT 텍스트
        topic: 주제
        safety_bans: 금지 키워드 리스트
        tool_context: 도구 컨텍스트
    
    Returns:
        안전 점수 및 감점 사유
    """
    score = 1.0
    reasons = []
    
    combined_text = f"{caption} {alt_text} {topic}".lower()
    
    # 1. safetyBans 매칭 확인
    if safety_bans:
        for banned_word in safety_bans:
            if banned_word.lower() in combined_text:
                # 중대/경미 판단 (간단히 길이로 구분)
                if len(banned_word) <= 4:
                    score -= 0.2
                    reasons.append(f"금지 키워드 '{banned_word}' 경미 매칭")
                else:
                    score -= 0.4
                    reasons.append(f"금지 키워드 '{banned_word}' 중대 매칭")
    
    # 2. 혐오/폭력/정치 선동/의학·금융 주장 감지
    harmful_patterns = [
        (r'\b(hate|kill|murder|attack|destroy)\b', '폭력적 표현'),
        (r'\b(racist|sexist|discriminat)\b', '차별적 표현'),
        (r'\b(cure|treatment|diagnos|medicine)\b', '의학적 주장'),
        (r'\b(invest|profit|stock|crypto|trading)\b', '금융적 주장'),
        (r'\b(vote|election|political|government)\b', '정치적 선동'),
    ]
    
    for pattern, reason in harmful_patterns:
        if re.search(pattern, combined_text):
            score -= 0.5
            reasons.append(f"부적절한 콘텐츠: {reason}")
    
    # 3. 과도 상업/허위 과장 감지
    commercial_patterns = [
        (r'\b(buy now|limited offer|sale|discount)\b', '과도한 상업 표현'),
        (r'\b(best|#1|guaranteed|amazing|incredible){3,}', '과장 표현'),
    ]
    
    for pattern, reason in commercial_patterns:
        if re.search(pattern, combined_text):
            score -= 0.15
            reasons.append(reason)
    
    # 4. 스팸성 해시태그/이모지 확인
    hashtag_count = caption.count('#')
    emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', caption))
    
    if hashtag_count > 5:
        score -= 0.2
        reasons.append(f"과도한 해시태그 ({hashtag_count}개)")
    
    if emoji_count > 5:
        score -= 0.1
        reasons.append(f"과도한 이모지 ({emoji_count}개)")
    
    # 점수 하한 설정
    score = max(0.0, score)
    
    return {
        'status': 'success',
        'score': round(score, 2),
        'reasons': reasons,
        'suitable_for_posting': score >= 0.7
    }

