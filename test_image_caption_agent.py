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

"""
이미지·캡션 생성 에이전트 테스트 파일

사용법:
    python test_image_caption_agent.py
"""

import asyncio
from image_caption_agent.schemas import ImageCaptionInput
from image_caption_agent.agent import generate_image_caption_content


async def test_basic_generation():
    """기본 이미지·캡션 생성 테스트"""
    print("=" * 60)
    print("테스트 1: 기본 생성 (한국어)")
    print("=" * 60)
    
    input_data = ImageCaptionInput(
        topic="커피와 아침의 여유",
        tone="friendly",
        locale="ko",
        hashtagsAllowed=2
    )
    
    print(f"\n입력:")
    print(f"  주제: {input_data.topic}")
    print(f"  톤: {input_data.tone}")
    print(f"  언어: {input_data.locale}")
    print(f"  해시태그 허용: {input_data.hashtagsAllowed}")
    
    try:
        output = await generate_image_caption_content(input_data)
        
        print(f"\n출력:")
        print(f"  캡션 ({len(output.caption)}자): {output.caption}")
        print(f"  ALT 텍스트 ({len(output.altText)}자): {output.altText}")
        print(f"  안전 점수: {output.safety.score}")
        
        if output.safety.reasons:
            print(f"  감점 사유:")
            for reason in output.safety.reasons:
                print(f"    - {reason}")
        
        if output.safety.score >= 0.7:
            print("\n✅ 게시에 적합한 콘텐츠입니다.")
        else:
            print("\n⚠️ 안전 점수가 낮아 검토가 필요합니다.")
        
        if output.imageBase64:
            print(f"\n📸 이미지 생성 완료 (Base64 길이: {len(output.imageBase64)})")
        else:
            print("\n⚠️ 이미지 생성 실패")
    
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")


async def test_english_generation():
    """영어 콘텐츠 생성 테스트"""
    print("\n\n" + "=" * 60)
    print("테스트 2: 영어 콘텐츠 (정보성)")
    print("=" * 60)
    
    input_data = ImageCaptionInput(
        topic="quantum computing breakthrough",
        tone="informative",
        locale="en",
        hashtagsAllowed=3
    )
    
    print(f"\n입력:")
    print(f"  Topic: {input_data.topic}")
    print(f"  Tone: {input_data.tone}")
    print(f"  Locale: {input_data.locale}")
    print(f"  Hashtags allowed: {input_data.hashtagsAllowed}")
    
    try:
        output = await generate_image_caption_content(input_data)
        
        print(f"\n출력:")
        print(f"  Caption ({len(output.caption)} chars): {output.caption}")
        print(f"  ALT text ({len(output.altText)} chars): {output.altText}")
        print(f"  Safety score: {output.safety.score}")
        
        if output.safety.score >= 0.7:
            print("\n✅ Suitable for posting.")
        else:
            print("\n⚠️ Safety score is low. Review required.")
            for reason in output.safety.reasons:
                print(f"    - {reason}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_safety_check():
    """안전성 체크 테스트 (금지 키워드)"""
    print("\n\n" + "=" * 60)
    print("테스트 3: 안전성 체크 (금지 키워드)")
    print("=" * 60)
    
    input_data = ImageCaptionInput(
        topic="weight loss miracle",
        tone="witty",
        locale="en",
        hashtagsAllowed=2,
        safetyBans=["miracle", "guaranteed", "cure"]
    )
    
    print(f"\n입력:")
    print(f"  Topic: {input_data.topic}")
    print(f"  Safety bans: {input_data.safetyBans}")
    
    try:
        output = await generate_image_caption_content(input_data)
        
        print(f"\n출력:")
        print(f"  Safety score: {output.safety.score}")
        print(f"  Reasons: {output.safety.reasons}")
        
        if output.safety.score >= 0.7:
            print("\n✅ Passed safety check.")
        else:
            print("\n⚠️ Failed safety check. Content needs review.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """메인 테스트 함수"""
    print("\n🚀 이미지·캡션 생성 에이전트 테스트 시작\n")
    
    # 테스트 1: 기본 생성 (한국어)
    await test_basic_generation()
    
    # 테스트 2: 영어 생성
    await test_english_generation()
    
    # 테스트 3: 안전성 체크
    await test_safety_check()
    
    print("\n\n" + "=" * 60)
    print("✅ 모든 테스트 완료")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

