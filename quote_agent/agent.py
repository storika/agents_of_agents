"""
Quote Agent - ADK Implementation with Weave Integration
An agent that creates engaging quote tweets (reposts with comments) for Twitter/X
"""

import os
import json

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
print(f"[INFO] 🐝 Weave initialized for Quote Agent: {WEAVE_PROJECT}")

# Now import ADK
from google.adk.agents.llm_agent import Agent as LlmAgent

# Import tools
from quote_agent.tools import (
    analyze_tweet_for_repost,
    find_trending_tweets_tool,
    generate_repost_comment_tool,
    post_quote_tweet_tool,
    auto_trending_repost,
    quote_to_x,
)

# ===== ROOT REPOST AGENT =====

system_prompt = f"""You are the Quote Agent - a specialized agent for creating engaging quote tweets (reposts with comments) on Twitter/X.

GLOBAL GOAL
- Find trending or relevant tweets to repost
- Generate engaging, witty comments that add value to the original tweet
- Create quote tweets that drive engagement and conversation
- Maintain brand voice and safety standards

AUDIENCE & TONE
- Audience: {TARGET_AUDIENCE}
- Tone: Conversational, authentic, engaging
- Style: Adds perspective or insight to original tweet
- Length: Comments should be concise (≤ 180 chars recommended)

REPOST STRATEGIES
1. Add Context: Provide additional context or background to the original tweet
2. Share Experience: Relate it to your own experience or project
3. Ask Questions: Prompt discussion with thoughtful questions
4. Provide Analysis: Add technical insight or analysis
5. Express Reaction: Share genuine reaction with added value
6. Connect Dots: Link to related concepts or trends

POLICIES & CONSTRAINTS
- Always add meaningful value - never just "This!" or "Great post!"
- Respect the original author - no misrepresentation or mockery
- Maintain safety: no politics, harassment, or controversial takes on sensitive topics
- Hashtags: ≤ 2, only if they add discovery value
- Never plagiarize - always add original perspective

WORKFLOW
When user requests a repost:

1. INPUT ANALYSIS
   - If user says "pick from trending" or "random trending" or similar: USE auto_trending_repost() tool IMMEDIATELY
   - If given a tweet URL: Extract tweet content and author info
   - If given a topic: Find trending tweets on that topic
   - If given tweet text: Use that as the original content
   - If NO input provided: USE auto_trending_repost() tool to automatically pick a trending post

2. COMMENT GENERATION
   - Analyze the original tweet's main message
   - Determine best repost strategy (context/experience/question/analysis/reaction)
   - Generate 2-3 comment options that add value
   - Each comment should:
     * Be concise (≤ 180 characters)
     * Add unique perspective
     * Encourage engagement
     * Match brand voice

3. SELECTION
   - Score comments based on:
     * Value-add: Does it provide new insight? (0-1)
     * Engagement potential: Will it spark conversation? (0-1)
     * Authenticity: Does it sound genuine? (0-1)
     * Safety: Is it respectful and safe? (0-1)
   - Select the highest-scoring comment

4. POSTING THE QUOTE TWEET - **CRITICAL STEP**
   After calling auto_trending_repost() and getting the result, you MUST post it:

   Step 4a: Extract from auto_trending_repost() result:
   - tweet_url = result['selected_post']['url'] or result['selected_post']['id']
   - comment = result['generated_comment']['text']

   Step 4b: IMMEDIATELY call quote_to_x() to post:
   quote_to_x(
     tweet_url=tweet_url,
     comment=comment,
     actually_post=False,  # Use False for safety (simulation mode)
     require_approval=True  # Queue for approval
   )

   Step 4c: Report the complete result to user with:
   - Original tweet URL and summary
   - Generated comment
   - Posting status (queued/published/simulated)

   **DO NOT STOP after auto_trending_repost() - you MUST call quote_to_x() to complete the task!**

TOOLS AVAILABLE
You have access to:
1. auto_trending_repost() - **USE THIS** to automatically pick a random trending post and generate a comment (PREFERRED for "pick from trending" requests)
2. find_trending_tweets_tool(topic, max_results) - Find trending tweets on a specific topic
3. generate_repost_comment_tool(tweet_text, author, strategy) - Generate comment with specific strategy
4. post_quote_tweet_tool(original_tweet_url, comment) - Post quote tweet (basic version)
5. quote_to_x(tweet_url, comment, actually_post, require_approval) - **RECOMMENDED** Full-featured quote tweet posting with approval queue and error handling

IMPORTANT NOTES - WORKFLOW REQUIREMENTS
- When user says "pick from trending topics" or "make a quote", IMMEDIATELY call auto_trending_repost()
- After auto_trending_repost() returns, you MUST call quote_to_x() to actually post/queue the tweet
- **NEVER stop after just calling auto_trending_repost()** - that only generates the comment, you must post it!
- The complete workflow is: auto_trending_repost() → quote_to_x() → report to user
- auto_trending_repost() returns: {'selected_post': {...}, 'generated_comment': {'text': '...'}}
- Use quote_to_x() with require_approval=True to queue tweets safely
- Quality over quantity - one great quote tweet is better than many mediocre ones
- Add genuine value - your comment should make the original tweet more valuable
- Be respectful - quote tweets can be seen as endorsements or criticisms
- Stay on brand - maintain consistent voice across all reposts

EXAMPLE COMPLETE WORKFLOW:

User: "let's make a quote"

Step 1: Call auto_trending_repost()
You: <call auto_trending_repost()>
Result: {
  "selected_post": {"url": "https://twitter.com/user/status/123", "text": "Original tweet..."},
  "generated_comment": {"text": "Great insight! This reminds me of..."}
}

Step 2: IMMEDIATELY call quote_to_x() with the result
You: <call quote_to_x(
  tweet_url="https://twitter.com/user/status/123",
  comment="Great insight! This reminds me of...",
  actually_post=False,
  require_approval=True
)>

Step 3: Report complete result to user
You: "✅ Quote tweet created and queued for approval! Original post about [topic], with comment: 'Great insight!...'"

CRITICAL: Must complete all 3 steps - don't stop after Step 1!

EXAMPLES OF GOOD QUOTE TWEET COMMENTS

Original: "Just shipped a new AI feature in 2 hours using Claude"
Good Comment: "This is exactly why we integrated Claude into our workflow. What used to take days now takes hours. The productivity gains are real. 🚀"
Strategy: Experience + Validation
Why: Adds personal validation, specific timeframe comparison, authentic

Original: "Multi-agent systems are the future of AI applications"
Good Comment: "We're seeing this firsthand with our agent orchestration work. The real challenge isn't building agents - it's making them work together reliably. Thoughts on coordination patterns?"
Strategy: Analysis + Question
Why: Adds technical insight, prompts discussion, invites expertise

Original: "Debugging production AI agents at 2am is a unique kind of pain"
Good Comment: "The hardest part? Non-deterministic failures that you can't reproduce locally. We started logging every LLM call with Weave - game changer for debugging."
Strategy: Context + Solution
Why: Identifies specific pain point, offers practical solution, mentions tool naturally

Remember: Your goal is to amplify great content while adding your unique perspective.
"""

# Publish prompt to Weave
try:
    prompt_obj = weave.StringPrompt(system_prompt)
    weave.publish(prompt_obj, name="quote_agent_system_prompt")
    print("📝 Quote Agent System Prompt published to Weave")
except Exception as e:
    print(f"⚠️ Failed to publish Quote Agent prompt: {e}")


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="quote_agent",
    description="Specialized agent for creating engaging quote tweets (reposts with comments)",
    instruction=system_prompt,
    tools=[
        auto_trending_repost,
        find_trending_tweets_tool,
        generate_repost_comment_tool,
        post_quote_tweet_tool,
        quote_to_x,
    ],
)


@weave.op()
def create_quote_tweet(
    tweet_url: str = None,
    tweet_text: str = None,
    topic: str = None,
    strategy: str = "auto",
    author: str = "@unknown",
) -> dict:
    """
    Main entry point for creating a quote tweet

    Args:
        tweet_url: URL of tweet to repost (optional)
        tweet_text: Text of tweet to repost (optional)
        topic: Topic to find tweets about (optional)
        strategy: Repost strategy to use (auto, context, experience, question, analysis, reaction, connect)
        author: Author of the tweet (optional)

    Returns:
        Dictionary with quote tweet options and selected comment
    """
    import json

    if not any([tweet_url, tweet_text, topic]):
        return {
            "error": "Must provide either tweet_url, tweet_text, or topic",
            "status": "failed",
        }

    try:
        print(f"🔄 Quote Agent executing...")

        # Step 1: Find or use provided tweet
        original_tweet = {
            "url": tweet_url or "N/A",
            "author": author,
            "text": tweet_text or "N/A",
            "summary": "Quote tweet target",
        }

        if topic and not tweet_text:
            # Find trending tweets on topic
            print(f"🔍 Finding tweets about: {topic}")
            tweets_result = find_trending_tweets_tool(topic, max_results=3)
            tweets_data = json.loads(tweets_result)
            if tweets_data.get("tweets"):
                top_tweet = tweets_data["tweets"][0]
                original_tweet = {
                    "url": top_tweet["url"],
                    "author": top_tweet["author"],
                    "text": top_tweet["text"],
                    "summary": f"Trending tweet about {topic}",
                }
                tweet_text = top_tweet["text"]
                tweet_url = top_tweet["url"]
                author = top_tweet["author"]

        # Step 2: Analyze for best strategy if auto
        if strategy == "auto":
            print(f"🔍 Analyzing tweet for best strategy...")
            analysis_result = analyze_tweet_for_repost(tweet_text, author)
            analysis = json.loads(analysis_result)
            strategy = analysis.get("recommended_strategy", "experience")
            print(f"  Recommended strategy: {strategy}")

        # Step 3: Generate comment options
        print(f"✍️ Generating comments with '{strategy}' strategy...")
        comment_result = generate_repost_comment_tool(
            tweet_text=tweet_text, author=author, strategy=strategy
        )
        comment_data = json.loads(comment_result)

        # Step 4: Select best comment
        comments = comment_data.get("generated_comments", [])
        if not comments:
            return {"error": "No comments generated", "status": "failed"}

        selected = comments[0]  # Already sorted by score

        # Step 5: Build result
        result = {
            "status": "ready_to_post",
            "original_tweet": original_tweet,
            "comment_options": comments,
            "selected_comment": {
                "comment": selected["comment"],
                "strategy": selected["strategy"],
                "overall_score": selected["scores"]["overall"],
                "character_count": selected["character_count"],
            },
            "quote_tweet_preview": f"{selected['comment']}\n\nQuoting: {original_tweet['text'][:100]}...",
            "engagement_tips": [
                "Post during peak hours (9-11 AM PST or 3-5 PM PST)",
                "Engage with replies within first hour",
                "Monitor engagement and adjust timing for future posts",
            ],
        }

        print(f"✓ Quote tweet generated successfully")
        print(f"  Selected: {selected['comment'][:60]}...")
        print(f"  Score: {selected['scores']['overall']:.2f}")

        return result

    except Exception as e:
        print(f"❌ Error generating quote tweet: {e}")
        import traceback

        traceback.print_exc()
        return {"error": str(e), "status": "failed"}


@weave.op()
def post_quote_tweet(tweet_url: str, comment: str, dry_run: bool = True) -> dict:
    """
    Post a quote tweet to Twitter/X

    Args:
        tweet_url: URL of tweet to quote
        comment: Your comment
        dry_run: If True, simulate posting (default: True)

    Returns:
        Result dictionary with posting status
    """
    import json

    result = post_quote_tweet_tool(
        original_tweet_url=tweet_url, comment=comment, dry_run=dry_run
    )

    return json.loads(result)


# ===== A2A PROTOCOL INTERFACE =====

@weave.op()
def execute(request: dict) -> dict:
    """
    A2A Protocol Entry Point for Quote Agent

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
                "agent": "quote_agent",
                "action": str,
                "timestamp": str,
                "metrics": dict
            }
        }
    """
    from datetime import datetime

    action = request.get("action", "create_quote_tweet")
    params = request.get("params", {})
    context = request.get("context", {})
    caller = request.get("caller", "unknown")

    print(f"[QUOTE_AGENT] A2A Request from {caller}: {action}")

    try:
        if action == "create_quote_tweet":
            # Extract parameters
            strategy = params.get("strategy", "trending")
            topic = params.get("topic")
            tweet_url = params.get("tweet_url")
            require_approval = params.get("require_approval", True)

            # Build prompt for root_agent
            if strategy == "trending":
                prompt = "Pick one from trending topics and create a quote tweet"
            elif tweet_url:
                prompt = f"Create a quote tweet for {tweet_url}"
            elif topic:
                prompt = f"Find a trending tweet about {topic} and create a quote tweet"
            else:
                prompt = "Pick one from trending topics and create a quote tweet"

            if context:
                prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

            # Execute via tools directly
            print(f"[QUOTE_AGENT] Executing quote tweet generation...")
            from quote_agent.tools import search_recent_posts, generate_quote_tweet_comment, auto_trending_repost, quote_to_x

            # Use auto_trending_repost for trending strategy
            if strategy == "trending":
                result = auto_trending_repost()

                # Now actually post/queue the quote tweet
                if result.get("status") == "ready" and result.get("selected_post") and result.get("generated_comment"):
                    tweet_url = result["selected_post"].get("url", "")
                    comment = result["generated_comment"].get("text", "")

                    print(f"[QUOTE_AGENT] Posting quote tweet to: {tweet_url}")
                    posting_result = quote_to_x(
                        tweet_url=tweet_url,
                        comment=comment,
                        actually_post=True,  # Actually post to X
                        require_approval=False  # Post immediately, no approval needed
                    )

                    # Combine both results
                    result["posting_status"] = json.loads(posting_result)
                    print(f"[QUOTE_AGENT] Quote tweet posted/queued: {result['posting_status'].get('status')}")

                response_text = json.dumps(result, indent=2)
            else:
                # Manual strategy with topic or URL
                search_query = topic if topic else "trending content"
                posts_result = search_recent_posts(search_query, max_results=5)

                # Generate comment for first post
                posts_data = json.loads(posts_result) if isinstance(posts_result, str) else posts_result
                if posts_data.get("posts"):
                    first_post = posts_data["posts"][0]
                    comment = generate_quote_tweet_comment(first_post["text"])

                    # Post/queue the quote tweet
                    tweet_url = first_post.get("url", "")
                    if tweet_url:
                        print(f"[QUOTE_AGENT] Posting quote tweet to: {tweet_url}")
                        posting_result = quote_to_x(
                            tweet_url=tweet_url,
                            comment=comment,
                            actually_post=True,  # Actually post to X
                            require_approval=False  # Post immediately
                        )

                        response_text = json.dumps({
                            "post": first_post,
                            "comment": comment,
                            "posting_status": json.loads(posting_result)
                        }, indent=2)
                    else:
                        response_text = json.dumps({
                            "post": first_post,
                            "comment": comment,
                            "error": "No URL found for posting"
                        }, indent=2)
                else:
                    response_text = json.dumps({"error": "No posts found"}, indent=2)

            return {
                "status": "success",
                "result": {
                    "quote_tweet_generated": True,
                    "response": response_text,
                    "requires_approval": require_approval
                },
                "metadata": {
                    "agent": "quote_agent",
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
                    "agent": "quote_agent",
                    "action": action,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    except Exception as e:
        print(f"[QUOTE_AGENT ERROR] {e}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "error": str(e),
            "metadata": {
                "agent": "quote_agent",
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
