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

from pydantic import BaseModel, Field
from typing import Optional


class VideoGenerationInput(BaseModel):
    """비디오 생성 입력 스키마"""

    image_path: str = Field(..., description="Reference image file path")
    concept: str = Field(..., description="Image concept/description")
    topic: str = Field(..., description="Content topic")
    tone: str = Field(default="engaging", description="Video tone (engaging, dramatic, calm, energetic)")
    duration: int = Field(default=8, description="Video duration in seconds (max 8)")
    aspect_ratio: str = Field(default="9:16", description="Video aspect ratio (9:16 for vertical, 16:9 for horizontal)")


class VideoGenerationOutput(BaseModel):
    """비디오 생성 출력 스키마"""

    status: str = Field(..., description="Generation status (success/failed)")
    video_path: Optional[str] = Field(None, description="Generated video file path")
    video_url: Optional[str] = Field(None, description="Video URL (if uploaded)")
    duration: int = Field(..., description="Video duration in seconds")
    aspect_ratio: str = Field(..., description="Video aspect ratio")
    motion_prompt: str = Field(..., description="Motion/story prompt used")
    generation_time: float = Field(..., description="Generation time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class VideoConceptOutput(BaseModel):
    """비디오 콘셉트 출력 스키마"""

    motion_prompt: str = Field(..., description="Detailed motion/cinematography prompt for video generation")
    camera_movement: str = Field(..., description="Camera movement description (zoom, pan, tilt, static)")
    visual_effects: str = Field(..., description="Visual effects or transitions")
    mood: str = Field(..., description="Overall mood and energy level")
    duration_plan: str = Field(..., description="How the 8 seconds will be structured")
