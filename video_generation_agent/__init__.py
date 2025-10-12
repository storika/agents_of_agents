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
Video Generation Agent

Generates short-form vertical videos (9:16) from images using Google Gemini Veo 3 API.
Designed for Instagram Reels, TikTok, and YouTube Shorts.
"""

from .agent import root_agent, video_generation_orchestrator
from .tools import generate_video_concept, generate_video_from_image

__all__ = [
    'root_agent',
    'video_generation_orchestrator',
    'generate_video_concept',
    'generate_video_from_image',
]
