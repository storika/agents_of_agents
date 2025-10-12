"""
Post Agent - ADK Implementation with Weave Integration
Specialized agent for creating and posting original tweets with images via A2A protocol
"""

import os
import json
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import weave

# Load environment variables
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ['WANDB_API_KEY'] = WANDB_API_KEY

WEAVE_PROJECT = os.getenv("WEAVE_PROJECT", "your-org/your-project")
TARGET_AUDIENCE = os.getenv("TARGET_AUDIENCE", "your target audience")
weave.init(WEAVE_PROJECT)
print(f"[INFO] 🐝 Weave initialized for Post Agent: {WEAVE_PROJECT}")

# Now import ADK
from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.agents.llm_agent import Agent as LlmAgent

# Import sub-agent management
from post_agent.sub_agents import (
    create_research_agent,
    create_creative_writer_agent,
    create_generator_agent,
    create_critic_agent,
    create_safety_agent,
    create_selector_agent,
    create_media_selector_agent,
    create_image_generator_agent,
    create_video_generator_agent
)

# Import tools for X posting
from post_agent.tools import post_to_x


# ===== SUB-AGENT PIPELINE =====

# Step 1: Research Agent (runs once)
research_agent = create_research_agent()

# Step 2: Content Generation Loop (Writer -> Generator -> Critic repeat)
content_loop = LoopAgent(
    name="ContentGenerationLoop",
    description="Iteratively generates 3 content variations through Writer -> Generator -> Critic cycle",
    sub_agents=[
        create_creative_writer_agent(),
        create_generator_agent(),
        create_critic_agent()
    ],
    max_iterations=3
)

# Step 3: Safety Agent (final validation)
safety_agent = create_safety_agent()

# Step 4: Selector Agent (final selection and guide)
selector_agent = create_selector_agent()

# Step 5: Media Selector (decides image vs video)
media_selector = create_media_selector_agent()

# Step 6: Image Generator (generates actual image from media_prompt)
image_generator = create_image_generator_agent()

# Step 7: Video Generator (generates video from image, optional)
video_generator = create_video_generator_agent()

# Pipeline: Research -> Loop -> Safety -> Selector -> Media Selection -> Image/Video Generation
content_pipeline = SequentialAgent(
    name="ContentPipeline",
    description="Sequential workflow: Research -> 3x Loop -> Safety -> Selection -> Media Type Decision -> Image/Video Generation",
    sub_agents=[
        research_agent,
        content_loop,
        safety_agent,
        selector_agent,
        media_selector,
        image_generator,
        video_generator
    ]
)


# ===== ROOT POST AGENT =====

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='post_agent',
    description='Specialized agent for creating original posts with images/videos for X/Twitter',
    tools=[post_to_x],
    instruction=f"""You are the Post Agent — a specialized agent for creating original tweets with images or videos.

GLOBAL GOAL:
Create high-quality, engaging original posts (text + image/video) optimized for X/Twitter.

AUDIENCE & TONE:
- Audience: {TARGET_AUDIENCE}
- Tone: engaging, authentic, professional yet approachable
- Length: ≤ 180 characters for main text
- Hashtags: ≤ 2, selected based on relevance and trends

CONTENT PIPELINE:
You have access to ContentPipeline sub-agent that handles:
1. Research Agent: Analyzes trends and audience
2. ContentGenerationLoop (3 iterations):
   - Creative Writer: Generates novel ideas
   - Generator: Creates actual shareable content with media_prompt
   - Critic: Evaluates quality
3. Safety Agent: Final validation
4. Selector Agent: Selects best from 3 candidates
5. Media Selector: Intelligently decides IMAGE vs VIDEO based on content
6. Image Generator: Creates actual 3:4 portrait image (Imagen)
7. Video Generator: Creates 8-second 9:16 vertical video (Veo 3, if selected)

WORKFLOW:
When user requests content creation (e.g., "create a post", "generate content"):

**PHASE 1: CONTENT GENERATION**
1. Check if topic specified:
   - If YES: Use the provided topic
   - If NO: Let Research Agent discover trending topics

2. Delegate to ContentPipeline sub-agent (it runs automatically):
   - Research identifies trends
   - Loop generates 3 content variations
   - Safety validates all 3
   - Selector chooses the BEST one
   - Media Selector decides IMAGE or VIDEO based on content
   - Image Generator creates image (always generated first)
   - Video Generator creates video from image (only if Media Selector chose VIDEO)

3. Review the final output (complete package):
   - Selected tweet text
   - Media type chosen (image or video)
   - Generated media file path (image: artifacts/generated_image_*.png, video: artifacts/generated_video_*.mp4)
   - Media decision reasoning
   - Performance prediction
   - Publishing guide

**PHASE 2: USER APPROVAL (MANDATORY)**
4. Present the complete content package to user:
   - Show final tweet text
   - Show media type selected and reasoning
   - Show generated media path (image_path or video_path)
   - Show performance predictions and scores
   - Show all 3 candidates summary for transparency
   - If video was selected, mention generation time (videos take 11s-6min)

5. **ASK FOR APPROVAL - MUST WAIT FOR USER**
   - ALWAYS ask: "이 콘텐츠를 X에 포스팅할까요? (승인하려면 'yes' 또는 '포스팅'이라고 답해주세요)"
   - **IMPORTANT**: WAIT for user response in the NEXT conversation turn
   - NEVER post automatically without explicit user confirmation

**PHASE 3: POSTING (ONLY AFTER USER APPROVAL)**
6. Post to X/Twitter (only when user explicitly approves):
   When user confirms (e.g., "yes", "포스팅", "post it"):
   - Determine media type from Media Selector output
   - Extract media_path (image_path or video_path) from generator output
   - Call post_to_x() tool with:
     * text: selected tweet text (without hashtags)
     * image_path: EXACT file path (for image OR video - both use same parameter)
     * hashtags: hashtag string (e.g., "Trending, News")
     * actually_post: True
   - Returns tweet_id and URL if successful
   - Show live tweet URL to user

OUTPUT FORMAT:
{{
  "status": "approved",
  "selected_content": {{
    "text": "Tweet text here...",
    "hashtags": ["Trending", "News"],
    "media_prompt": "Visual concept description...",
    "platform": "X",
    "character_count": 125
  }},
  "media_decision": {{
    "media_type": "image|video",
    "reasoning": "Static visual works best for this concept...",
    "generation_time_estimate": "2-5 seconds"
  }},
  "generated_media": {{
    "status": "success",
    "media_type": "image|video",
    "image_path": "artifacts/generated_image_20251012_153045.png",
    "video_path": "artifacts/generated_video_20251012_153100.mp4",  // if video selected
    "aspect_ratio": "3:4|9:16",
    "generation_time": "float (actual time in seconds)"
  }},
  "scores": {{
    "clarity": 0.88,
    "novelty": 0.85,
    "shareability": 0.92,
    "credibility": 0.75,
    "safety": 1.0,
    "overall": 0.87
  }},
  "reasoning": "Selected for highest shareability...",
  "performance_prediction": "Expected 8.5-9% engagement...",
  "publishing_guide": {{
    "recommended_time": "9-11 AM PST or 3-5 PM PST",
    "engagement_tips": [...]
  }}
}}

IMPORTANT:
- Do NOT ask for topic/tone if user just says "create post" or similar
- ALWAYS ask for approval before posting
- The agent will intelligently choose between image and video
- Video generation takes 11s-6min (image is faster: 2-5s)
- Extract correct media_path based on media_type
- Keep text and hashtags separate (tool will merge them)
""",
    sub_agents=[content_pipeline]
)


# ===== A2A PROTOCOL INTERFACE =====

def execute(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    A2A Protocol Entry Point for Post Agent

    Args:
        request: {
            "action": str,              # Action to perform
            "params": dict,             # Action-specific parameters
            "context": dict,            # Historical data, trends, etc.
            "caller": str               # Who's calling (for tracking)
        }

    Returns:
        {
            "status": "success|pending|failed",
            "result": Any,              # Action result
            "metadata": {
                "agent": "post_agent",
                "action": str,
                "timestamp": str,
                "metrics": dict
            }
        }
    """
    action = request.get("action", "create_post")
    params = request.get("params", {})
    context = request.get("context", {})
    caller = request.get("caller", "unknown")

    print(f"[POST_AGENT] A2A Request from {caller}: {action}")

    try:
        if action == "create_post":
            # Extract parameters
            topic = params.get("topic")
            tone = params.get("tone", "witty")
            require_approval = params.get("require_approval", True)

            # Build prompt for root_agent
            prompt = "Create an original post"
            if topic:
                prompt += f" about {topic}"
            if tone:
                prompt += f" with {tone} tone"
            if context:
                prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

            # Execute via content_pipeline tools
            print(f"[POST_AGENT] Executing ContentPipeline...")
            from post_agent.sub_agents import (
                call_research_layer,
                call_creative_writer_layer,
                call_generator_layer,
                generate_image_concept,
                generate_video_concept
            )
            from post_agent.tools import generate_twitter_image, generate_video_from_image

            # Pipeline execution: Research -> Writer -> Generator
            research_result = call_research_layer(topic or "trending topics")
            writer_result = call_creative_writer_layer(research_result)
            generator_result = call_generator_layer(writer_result)

            # Extract media_prompt from generator
            media_prompt = None
            media_path = None
            media_type = "none"

            if generator_result and "content_pieces" in generator_result:
                content_pieces = generator_result.get("content_pieces", [])
                if content_pieces:
                    first_piece = content_pieces[0]
                    media_prompt = first_piece.get("media_prompt", "")

                    # Decide whether to generate image or video
                    # For now, default to image (simple logic - can be enhanced later)
                    user_requested_video = "video" in str(params).lower() or "video" in str(context).lower()

                    if media_prompt:
                        print(f"[POST_AGENT] Generating media from prompt: {media_prompt[:80]}...")

                        # Generate image first (always needed, even for video)
                        image_result = generate_twitter_image(concept=media_prompt)

                        if image_result.get("status") == "success":
                            image_path = image_result.get("file_path")
                            media_path = image_path
                            media_type = "image"
                            print(f"[POST_AGENT] Image generated: {image_path}")

                            # If video requested, generate video from image
                            if user_requested_video and image_path:
                                print(f"[POST_AGENT] User requested video, generating from image...")

                                # Generate motion prompt
                                video_concept_result = generate_video_concept(
                                    image_concept=media_prompt,
                                    topic=topic or "general",
                                    tone=tone
                                )

                                if video_concept_result.get("status") == "success":
                                    motion_prompt = video_concept_result.get("motion_prompt")

                                    # Generate video
                                    video_result = generate_video_from_image(
                                        image_path=image_path,
                                        motion_prompt=motion_prompt,
                                        aspect_ratio="9:16",
                                        duration=8
                                    )

                                    if video_result.get("status") == "success":
                                        media_path = video_result.get("video_path")
                                        media_type = "video"
                                        print(f"[POST_AGENT] Video generated: {media_path}")
                                    else:
                                        print(f"[POST_AGENT] Video generation failed, using image instead")
                                else:
                                    print(f"[POST_AGENT] Video concept generation failed, using image only")
                        else:
                            print(f"[POST_AGENT] Image generation failed: {image_result.get('reason')}")

            response_text = json.dumps(generator_result, indent=2)

            # Extract content and actually post it
            posting_result = None
            if generator_result and "content_pieces" in generator_result:
                content_pieces = generator_result.get("content_pieces", [])
                if content_pieces:
                    # Get the first content piece (for X/Twitter)
                    first_piece = content_pieces[0]
                    tweet_text = first_piece.get("content", "")
                    hashtags = " ".join(f"#{tag}" for tag in first_piece.get("hashtags", []))

                    # Combine text and hashtags
                    full_text = f"{tweet_text} {hashtags}".strip()

                    print(f"[POST_AGENT] Posting to X: {full_text[:80]}...")
                    if media_path:
                        print(f"[POST_AGENT] Including media ({media_type}): {media_path}")

                    # Actually post to X
                    posting_result = post_to_x(
                        text=full_text,
                        image_path=media_path or "",  # Use generated media (image or video)
                        hashtags="",  # Already included in text
                        actually_post=True  # Always post immediately
                    )

                    print(f"[POST_AGENT] Posting result: {posting_result}")

            return {
                "status": "success",
                "result": {
                    "content_generated": True,
                    "media_generated": media_path is not None,
                    "media_type": media_type,
                    "media_path": media_path,
                    "content_posted": posting_result is not None,
                    "posting_result": posting_result,
                    "response": response_text,
                    "requires_approval": require_approval
                },
                "metadata": {
                    "agent": "post_agent",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": {
                        "generation_time_ms": 0  # TODO: Track actual time
                    }
                }
            }

        else:
            return {
                "status": "failed",
                "error": f"Unknown action: {action}",
                "metadata": {
                    "agent": "post_agent",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    except Exception as e:
        print(f"[POST_AGENT ERROR] {e}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "error": str(e),
            "metadata": {
                "agent": "post_agent",
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


# ===== CONVENIENCE FUNCTIONS =====

def create_post(
    topic: str = None,
    tone: str = "witty",
    context: Dict[str, Any] = None,
    caller: str = "direct"
) -> Dict[str, Any]:
    """
    Convenience function for creating posts

    Args:
        topic: Content topic (optional, will discover from trends if None)
        tone: Content tone (witty, informative, minimal, friendly)
        context: Historical performance data for learning
        caller: Who's calling (for tracking)

    Returns:
        A2A response dict
    """
    request = {
        "action": "create_post",
        "params": {
            "topic": topic,
            "tone": tone,
            "require_approval": True
        },
        "context": context or {},
        "caller": caller
    }

    return execute(request)


# Publish prompt to Weave
try:
    prompt_obj = weave.StringPrompt(root_agent.instruction)
    weave.publish(prompt_obj, name="post_agent_system_prompt")
    print("📝 Post Agent System Prompt published to Weave")
except Exception as e:
    print(f"⚠️ Failed to publish Post Agent prompt: {e}")
