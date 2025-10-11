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

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ImageCaptionInput(BaseModel):
    """입력 스키마: 이미지·캡션 생성을 위한 요청 데이터"""
    topic: str = Field(..., description="이미지와 캡션의 주제")
    tone: Literal["friendly", "witty", "informative", "minimal"] = Field(
        default="friendly", 
        description="캡션 톤"
    )
    locale: str = Field(default="en", description="언어 코드 (예: en, ko, ja)")
    hashtagsAllowed: int = Field(
        default=2, 
        ge=0, 
        le=5, 
        description="허용되는 최대 해시태그 개수"
    )
    safetyBans: Optional[list[str]] = Field(
        default=None, 
        description="금지된 키워드 리스트"
    )


class SafetyScore(BaseModel):
    """안전 점수 스키마"""
    score: float = Field(..., ge=0.0, le=1.0, description="안전 점수 (0~1, 높을수록 안전)")
    reasons: list[str] = Field(default_factory=list, description="감점 사유")


class ImageCaptionOutput(BaseModel):
    """출력 스키마: 생성된 이미지·캡션·ALT 텍스트 및 안전 점수"""
    imageBase64: str = Field(..., description="Base64로 인코딩된 이미지 (artifact에서 로드)")
    caption: str = Field(..., max_length=280, description="트위터용 캡션 (≤280자)")
    altText: str = Field(..., min_length=80, max_length=120, description="ALT 텍스트 (80-120자)")
    safety: SafetyScore = Field(..., description="안전 점수 및 사유")

