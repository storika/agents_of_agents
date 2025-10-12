"""
Repost Agent - ADK Implementation with Weave Integration
An agent that reposts (retweets) tweets without comments on Twitter/X
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

WEAVE_PROJECT = os.getenv("WEAVE_PROJECT", "your-org/your-project")
TARGET_AUDIENCE = os.getenv("TARGET_AUDIENCE", "your target audience")
weave.init(WEAVE_PROJECT)
print(f"[INFO] 🐝 Weave initialized for Repost Agent: {WEAVE_PROJECT}")

# Now import ADK
from google.adk.agents.llm_agent import Agent as LlmAgent

# Import tools
from repost_agent.tools import (
    analyze_tweet_for_repost,
    repost_tweet
)

# ===== ROOT REPOST AGENT =====

system_prompt = f"""You are the Repost Agent - a specialized agent for reposting (retweeting) tweets without comments on Twitter/X.

GLOBAL GOAL:
- Find valuable tweets to amplify
- Repost content that aligns with brand and audience
- Build curation credibility
- Support the community by amplifying good content

AUDIENCE & TONE:
- Audience: {TARGET_AUDIENCE}
- Purpose: Curate and amplify valuable content
- Strategy: Be selective - only repost high-quality, relevant content

REPOST CRITERIA:
1. Alignment: Content aligns with brand values and expertise
2. Quality: High-quality, valuable information
3. Relevance: Relevant to target audience
4. Authority: From credible sources or contains verified information
5. Timeliness: Current and timely content

POLICIES & CONSTRAINTS:
- Be highly selective - quality over quantity
- Only repost content that adds value to followers
- Verify content aligns with brand before reposting
- No spam, controversial, or low-quality content
- Maintain safety: no politics, harassment, or sensitive topics

WORKFLOW:
When user requests a repost:

1. INPUT ANALYSIS:
   - If given a tweet URL: Analyze the tweet for repost worthiness
   - If given a topic: Find trending tweets on that topic to repost
   - Evaluate content quality and alignment

2. ALIGNMENT CHECK:
   - Does this content align with our brand? (AI/ML, dev tools, building, transparency)
   - Is it high quality and valuable?
   - Is it from a credible source?
   - Is it timely and relevant?
   - Would our audience benefit from seeing this?

3. DECISION:
   - Score alignment: 0-1 (how well it aligns with brand)
   - Score quality: 0-1 (content quality)
   - Score relevance: 0-1 (audience relevance)
   - Overall threshold: >= 0.80 to repost

4. REPOSTING:
   - If scores pass threshold, repost immediately
   - If below threshold, explain why not reposting
   - Return repost status and URL

OUTPUT FORMAT:
{
  "original_tweet": {
    "url": "https://twitter.com/user/status/123",
    "author": "@username",
    "text": "Original tweet text...",
    "summary": "Brief content summary"
  },
  "analysis": {
    "alignment_score": 0.92,
    "quality_score": 0.88,
    "relevance_score": 0.90,
    "overall_score": 0.90,
    "reasoning": "High-quality technical content about AI agents, aligns perfectly with brand"
  },
  "decision": "repost|skip",
  "status": "ready_to_repost|skipped"
}

TOOLS AVAILABLE:
1. analyze_tweet_for_repost(tweet_url) - Analyze tweet for repost worthiness
2. repost_tweet(tweet_url, dry_run) - Actually repost the tweet

IMPORTANT NOTES:
- Be highly selective - only repost the best content
- Quality and alignment are paramount
- When in doubt, don't repost
- Simple repost without comment - let the content speak for itself
- This is about curation, not just amplification

EXAMPLES OF REPOST-WORTHY CONTENT:

✅ GOOD TO REPOST:
- "New research on multi-agent coordination patterns in production systems" (relevant, high-quality)
- "Just open-sourced our agent orchestration framework" (valuable, community contribution)
- "Fascinating breakdown of how Claude handles context windows" (educational, on-brand)

❌ NOT GOOD TO REPOST:
- "My product is the best!" (self-promotional spam)
- Generic motivational quotes (low value)
- Controversial takes on non-technical topics (off-brand)
- Low-effort content without substance

Remember: Your repost is an endorsement. Only amplify content you'd be proud to associate with.
"""

# Publish prompt to Weave
try:
    prompt_obj = weave.StringPrompt(system_prompt)
    weave.publish(prompt_obj, name="repost_agent_system_prompt")
    print("📝 Repost Agent System Prompt published to Weave")
except Exception as e:
    print(f"⚠️ Failed to publish Repost Agent prompt: {e}")


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="repost_agent",
    description="Specialized agent for reposting high-quality tweets without comments",
    instruction=system_prompt,
    tools=[
        analyze_tweet_for_repost,
        repost_tweet
    ],
)


# ===== A2A PROTOCOL INTERFACE =====

@weave.op()
def execute(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    A2A Protocol Entry Point for Repost Agent

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
    action = request.get("action", "repost")
    params = request.get("params", {})
    context = request.get("context", {})
    caller = request.get("caller", "unknown")

    print(f"[REPOST_AGENT] A2A Request from {caller}: {action}")

    try:
        if action == "repost":
            tweet_url = params.get("tweet_url")
            require_approval = params.get("require_approval", True)

            if not tweet_url:
                return {
                    "status": "failed",
                    "error": "tweet_url is required",
                    "metadata": {
                        "agent": "repost_agent",
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
                        "agent": "repost_agent",
                        "action": action,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }

            # Build prompt
            prompt = f"Analyze and repost the tweet at {tweet_url}"
            if context:
                prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

            # Execute via tools directly
            print(f"[REPOST_AGENT] Analyzing tweet for repost...")
            from repost_agent.tools import analyze_tweet_for_repost, repost_tweet

            # Analyze the tweet
            analysis_str = analyze_tweet_for_repost(tweet_url)
            analysis = json.loads(analysis_str)

            # Perform repost (always post immediately)
            repost_result_str = repost_tweet(tweet_url, dry_run=False)
            response_text = repost_result_str

            return {
                "status": "success",
                "result": {
                    "repost_analyzed": True,
                    "response": response_text,
                    "requires_approval": require_approval
                },
                "metadata": {
                    "agent": "repost_agent",
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
                    "agent": "repost_agent",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    except Exception as e:
        print(f"[REPOST_AGENT ERROR] {e}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "error": str(e),
            "metadata": {
                "agent": "repost_agent",
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


# ===== CONVENIENCE FUNCTIONS =====

@weave.op()
def simple_repost(
    tweet_url: str,
    context: Dict[str, Any] = None,
    caller: str = "direct"
) -> Dict[str, Any]:
    """
    Convenience function for reposting

    Args:
        tweet_url: URL of tweet to repost
        context: Additional context
        caller: Who's calling

    Returns:
        A2A response dict
    """
    request = {
        "action": "repost",
        "params": {
            "tweet_url": tweet_url,
            "require_approval": True
        },
        "context": context or {},
        "caller": caller
    }

    return execute(request)
