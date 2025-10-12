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

weave.init("mason-choi-storika/WeaveHacks2")
print("[INFO] 🐝 Weave initialized for Post Agent: mason-choi-storika/WeaveHacks2")

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
    create_image_generator_agent
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

# Step 5: Image Generator (generates actual image from media_prompt)
image_generator = create_image_generator_agent()

# Pipeline: Research -> Loop -> Safety -> Selector -> Image Generation
content_pipeline = SequentialAgent(
    name="ContentPipeline",
    description="Sequential workflow: Research -> 3x Loop -> Safety -> Selection -> Image Generation",
    sub_agents=[
        research_agent,
        content_loop,
        safety_agent,
        selector_agent,
        image_generator
    ]
)


# ===== ROOT POST AGENT =====

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='post_agent',
    description='Specialized agent for creating original posts with images for X/Twitter',
    tools=[post_to_x],
    instruction="""You are the Post Agent — a specialized agent for creating original tweets with images.

GLOBAL GOAL:
Create high-quality, engaging original posts (text + image) optimized for X/Twitter.

AUDIENCE & TONE:
- Audience: AI/ML developers, indie hackers, founders
- Tone: builder-friendly, witty-but-respectful, transparent
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
5. Image Generator: Creates actual 3:4 image from selected media_prompt

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
   - Image Generator creates ACTUAL image from media_prompt

3. Review the final output (complete package):
   - Selected tweet text
   - Generated image file path (e.g., artifacts/generated_image_20251012_153045.png)
   - Performance prediction
   - Publishing guide

**PHASE 2: USER APPROVAL (MANDATORY)**
4. Present the complete content package to user:
   - Show final tweet text
   - Show generated image path (from Image Generator's "image_path" field)
   - Show performance predictions and scores
   - Show all 3 candidates summary for transparency

5. **ASK FOR APPROVAL - MUST WAIT FOR USER**
   - ALWAYS ask: "이 콘텐츠를 X에 포스팅할까요? (승인하려면 'yes' 또는 '포스팅'이라고 답해주세요)"
   - **IMPORTANT**: WAIT for user response in the NEXT conversation turn
   - NEVER post automatically without explicit user confirmation

**PHASE 3: POSTING (ONLY AFTER USER APPROVAL)**
6. Post to X/Twitter (only when user explicitly approves):
   When user confirms (e.g., "yes", "포스팅", "post it"):
   - Extract image_path from Image Generator output
   - Call post_to_x() tool with:
     * text: selected tweet text (without hashtags)
     * image_path: EXACT file path from Image Generator
     * hashtags: hashtag string (e.g., "BuildInPublic, AIAgents")
     * actually_post: True
   - Returns tweet_id and URL if successful
   - Show live tweet URL to user

OUTPUT FORMAT:
{
  "status": "approved",
  "selected_content": {
    "text": "Tweet text here...",
    "hashtags": ["BuildInPublic", "AIAgents"],
    "media_prompt": "Visual concept description...",
    "platform": "X",
    "character_count": 125
  },
  "generated_media": {
    "status": "success",
    "image_path": "artifacts/generated_image_20251012_153045.png",
    "aspect_ratio": "3:4"
  },
  "scores": {
    "clarity": 0.88,
    "novelty": 0.85,
    "shareability": 0.92,
    "credibility": 0.75,
    "safety": 1.0,
    "overall": 0.87
  },
  "reasoning": "Selected for highest shareability...",
  "performance_prediction": "Expected 8.5-9% engagement...",
  "publishing_guide": {
    "recommended_time": "9-11 AM PST or 3-5 PM PST",
    "engagement_tips": [...]
  }
}

IMPORTANT:
- Do NOT ask for topic/tone if user just says "create post" or similar
- ALWAYS ask for approval before posting
- Extract image_path from Image Generator output correctly
- Keep text and hashtags separate (tool will merge them)
""",
    sub_agents=[content_pipeline]
)


# ===== A2A PROTOCOL INTERFACE =====

@weave.op()
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
            from post_agent.sub_agents import call_research_layer, call_creative_writer_layer, call_generator_layer

            # Simple execution: Research -> Writer -> Generator
            research_result = call_research_layer(topic or "trending topics")
            writer_result = call_creative_writer_layer(research_result)
            generator_result = call_generator_layer(writer_result)

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

                    # Actually post to X
                    posting_result = post_to_x(
                        text=full_text,
                        image_path="",  # No image for now
                        hashtags="",  # Already included in text
                        actually_post=True  # Always post immediately
                    )

                    print(f"[POST_AGENT] Posting result: {posting_result}")

            return {
                "status": "success",
                "result": {
                    "content_generated": True,
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

@weave.op()
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
