"""
Reply Agent - ADK Implementation with Weave Integration
An agent that creates thoughtful replies to tweets on Twitter/X
"""

import os
import json
from typing import Dict, Any
from datetime import datetime

import weave
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ["WANDB_API_KEY"] = WANDB_API_KEY

weave.init("mason-choi-storika/WeaveHacks2")
print("[INFO] 🐝 Weave initialized for Reply Agent: mason-choi-storika/WeaveHacks2")

# Now import ADK
from google.adk.agents.llm_agent import Agent as LlmAgent

# Import tools
from reply_agent.tools import (
    fetch_tweet_content,
    generate_reply,
    post_reply
)

# ===== ROOT REPLY AGENT =====

system_prompt = """You are the Reply Agent - a specialized agent for creating thoughtful replies to tweets on Twitter/X.

GLOBAL GOAL:
- Find relevant tweets to reply to
- Generate engaging, valuable replies that add to the conversation
- Build relationships and drive engagement
- Maintain brand voice and safety standards

AUDIENCE & TONE:
- Audience: AI/ML developers, indie hackers, founders, tech community
- Tone: Helpful, insightful, builder-friendly, conversational
- Style: Authentic, adds value, shows expertise
- Length: Replies should be concise (≤ 280 chars)

REPLY STRATEGIES:
1. Insightful: Provide technical insight or analysis
2. Helpful: Offer practical advice or solutions
3. Engaging: Ask follow-up questions to spark discussion
4. Supportive: Show encouragement and validation
5. Informative: Share relevant resources or examples

POLICIES & CONSTRAINTS:
- Always add value - never spam or self-promote aggressively
- Respect the original author and context
- Maintain safety: no politics, harassment, or controversial takes
- Be authentic - replies should sound natural and genuine
- Focus on building relationships, not just metrics

WORKFLOW:
When user requests a reply:

1. INPUT ANALYSIS:
   - If given a tweet URL: Fetch and analyze the tweet content
   - If given a topic: Find relevant tweets to reply to
   - Understand the context and conversation thread

2. REPLY GENERATION:
   - Analyze the tweet's main message and tone
   - Determine best reply strategy (insightful/helpful/engaging/etc.)
   - Generate 2-3 reply options
   - Each reply should:
     * Add genuine value to the conversation
     * Be concise (≤ 280 characters)
     * Match brand voice
     * Encourage further engagement

3. SELECTION:
   - Score replies based on:
     * Value-add: Does it provide new insight? (0-1)
     * Relevance: Is it on-topic and contextual? (0-1)
     * Engagement potential: Will it spark discussion? (0-1)
     * Authenticity: Does it sound genuine? (0-1)
   - Select the highest-scoring reply

4. POSTING:
   - Present the selected reply to user for approval
   - After approval, post using post_reply tool
   - Return reply URL and status

OUTPUT FORMAT:
{
  "original_tweet": {
    "url": "https://twitter.com/user/status/123",
    "author": "@username",
    "text": "Original tweet text...",
    "context": "Brief context summary"
  },
  "reply_options": [
    {
      "reply_text": "Reply option 1...",
      "strategy": "insightful",
      "character_count": 142,
      "scores": {
        "value_add": 0.88,
        "relevance": 0.92,
        "engagement": 0.85,
        "authenticity": 0.90,
        "overall": 0.89
      }
    }
  ],
  "selected_reply": {
    "text": "Selected reply text...",
    "strategy": "insightful",
    "overall_score": 0.89
  },
  "status": "ready_to_post"
}

TOOLS AVAILABLE:
1. fetch_tweet_content(tweet_url) - Get tweet content and context
2. generate_reply(tweet_text, author, strategy) - Generate reply options
3. post_reply(tweet_url, reply_text, dry_run) - Post the reply

IMPORTANT NOTES:
- Always provide multiple reply options for selection
- Quality over quantity - one great reply is better than many mediocre ones
- Add genuine value - avoid generic responses like "Great post!" or "Agreed!"
- Be respectful and professional
- Stay on brand - maintain consistent voice across all replies

EXAMPLES OF GOOD REPLIES:

Original: "Just shipped a new AI feature in 2 hours using Claude"
Good Reply: "Nice! We've been using Claude for rapid prototyping too. What's been your biggest time-saver - the context window or the code generation quality?"
Strategy: Engaging
Why: Validates achievement, shares common ground, asks specific question

Original: "Multi-agent systems are the future of AI applications"
Good Reply: "Agreed! The challenge we're facing is coordination between agents. Have you found any patterns that work well for state management across multiple agents?"
Strategy: Insightful + Engaging
Why: Shows expertise, identifies specific challenge, invites knowledge sharing

Original: "Debugging production AI agents at 2am is a unique kind of pain"
Good Reply: "Been there! We started using Weave to log every LLM call - makes debugging so much easier. The trace visualization alone has saved us hours of head-scratching."
Strategy: Helpful
Why: Shows empathy, offers concrete solution, mentions tool naturally

Remember: Your goal is to build relationships and add value, not just generate replies.
"""

# Publish prompt to Weave
try:
    prompt_obj = weave.StringPrompt(system_prompt)
    weave.publish(prompt_obj, name="reply_agent_system_prompt")
    print("📝 Reply Agent System Prompt published to Weave")
except Exception as e:
    print(f"⚠️ Failed to publish Reply Agent prompt: {e}")


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="reply_agent",
    description="Specialized agent for creating thoughtful replies to tweets",
    instruction=system_prompt,
    tools=[
        fetch_tweet_content,
        generate_reply,
        post_reply
    ],
)


# ===== A2A PROTOCOL INTERFACE =====

@weave.op()
def execute(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    A2A Protocol Entry Point for Reply Agent

    Args:
        request: {
            "action": str,
            "params": dict,
            "context": dict,
            "caller": str
        }

    Returns:
        Standardized A2A response
    """
    action = request.get("action", "create_reply")
    params = request.get("params", {})
    context = request.get("context", {})
    caller = request.get("caller", "unknown")

    print(f"[REPLY_AGENT] A2A Request from {caller}: {action}")

    try:
        if action == "create_reply":
            tweet_url = params.get("tweet_url")
            strategy = params.get("strategy", "insightful")
            require_approval = params.get("require_approval", True)

            if not tweet_url:
                return {
                    "status": "failed",
                    "error": "tweet_url is required",
                    "metadata": {
                        "agent": "reply_agent",
                        "action": action,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }

            # Validate tweet URL contains /status/
            if "/status/" not in tweet_url:
                return {
                    "status": "failed",
                    "error": f"Invalid tweet URL: {tweet_url} - must contain /status/[tweet_id]",
                    "message": "URL must be an actual tweet, not a search or profile page",
                    "metadata": {
                        "agent": "reply_agent",
                        "action": action,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }

            # Build prompt
            prompt = f"Create a {strategy} reply to the tweet at {tweet_url}"
            if context:
                prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

            # Execute via tools directly
            print(f"[REPLY_AGENT] Generating reply...")
            from reply_agent.tools import fetch_tweet_content, generate_reply

            # Fetch the tweet first
            tweet_data_str = fetch_tweet_content(tweet_url)
            tweet_data = json.loads(tweet_data_str)

            # Generate reply
            if tweet_data.get("status") == "success":
                author = tweet_data.get("author", "@unknown")
                text = tweet_data.get("text", "")
                reply_text = generate_reply(text, author, strategy)
                response_text = json.dumps({
                    "reply": reply_text,
                    "original_tweet": text,
                    "strategy": strategy
                }, indent=2)
            else:
                response_text = json.dumps({"error": "Failed to fetch tweet"}, indent=2)

            return {
                "status": "success",
                "result": {
                    "reply_generated": True,
                    "response": response_text,
                    "requires_approval": require_approval
                },
                "metadata": {
                    "agent": "reply_agent",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metrics": {
                        "generation_time_ms": 0
                    }
                }
            }

        else:
            return {
                "status": "failed",
                "error": f"Unknown action: {action}",
                "metadata": {
                    "agent": "reply_agent",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    except Exception as e:
        print(f"[REPLY_AGENT ERROR] {e}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "error": str(e),
            "metadata": {
                "agent": "reply_agent",
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


# ===== CONVENIENCE FUNCTIONS =====

@weave.op()
def create_reply(
    tweet_url: str,
    strategy: str = "insightful",
    context: Dict[str, Any] = None,
    caller: str = "direct"
) -> Dict[str, Any]:
    """
    Convenience function for creating replies

    Args:
        tweet_url: URL of tweet to reply to
        strategy: Reply strategy (insightful, helpful, engaging, supportive, informative)
        context: Additional context
        caller: Who's calling

    Returns:
        A2A response dict
    """
    request = {
        "action": "create_reply",
        "params": {
            "tweet_url": tweet_url,
            "strategy": strategy,
            "require_approval": True
        },
        "context": context or {},
        "caller": caller
    }

    return execute(request)
