"""
Quote Agent - ADK Implementation with Weave Integration
An agent that creates engaging quote tweets (reposts with comments) for Twitter/X
"""

import os

import weave
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ["WANDB_API_KEY"] = WANDB_API_KEY

weave.init("mason-choi-storika/WeaveHacks2")
print("[INFO] 🐝 Weave initialized for Quote Agent: mason-choi-storika/WeaveHacks2")

# Now import ADK
from google.adk.agents.llm_agent import Agent as LlmAgent

# Import tools
from quote_agent.tools import (
    analyze_tweet_for_repost,
    find_trending_tweets_tool,
    generate_repost_comment_tool,
    post_quote_tweet_tool,
    auto_trending_repost,
)

# ===== ROOT REPOST AGENT =====

system_prompt = """You are the Quote Agent - a specialized agent for creating engaging quote tweets (reposts with comments) on Twitter/X.

GLOBAL GOAL
- Find trending or relevant tweets to repost
- Generate engaging, witty comments that add value to the original tweet
- Create quote tweets that drive engagement and conversation
- Maintain brand voice and safety standards

AUDIENCE & TONE
- Audience: AI/ML developers, indie hackers, founders, tech community
- Tone: Conversational, witty-but-respectful, builder-friendly
- Style: Authentic, adds perspective or insight to original tweet
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

4. POSTING THE REPOST
   After calling auto_trending_repost() and getting the result:
   - Extract the post ID and comment from the result
   - AUTOMATICALLY call post_quote_tweet_tool(post_id, comment, dry_run=True) to post it
   - Present the final result to the user with posting status

   For manual repost requests, return JSON with:
   {
     "original_tweet": {
       "url": "https://twitter.com/user/status/123",
       "text": "Original tweet text...",
       "summary": "Brief summary of main point"
     },
     "selected_comment": {
       "comment": "Selected comment text",
       "character_count": 142
     },
     "quote_tweet_preview": "How your quote tweet will appear",
     "status": "ready_to_post"
   }

TOOLS AVAILABLE
You have access to:
1. auto_trending_repost() - **USE THIS** to automatically pick a random trending post and generate a comment (PREFERRED for "pick from trending" requests)
2. find_trending_tweets_tool(topic, max_results) - Find trending tweets on a specific topic
3. generate_repost_comment_tool(tweet_text, author, strategy) - Generate comment with specific strategy
4. post_quote_tweet_tool(original_tweet_url, comment) - Actually post the quote tweet

IMPORTANT NOTES
- When user says "pick from trending topics" or similar, IMMEDIATELY call auto_trending_repost() - do NOT ask for a topic
- After auto_trending_repost() returns, IMMEDIATELY call post_quote_tweet_tool() with the result
- auto_trending_repost() returns a dict with 'selected_post' (containing 'id') and 'generated_comment' (containing 'text')
- Extract result['selected_post']['id'] and result['generated_comment']['text'] to call post_quote_tweet_tool
- Always provide options - let the system or user choose the best comment
- Quality over quantity - one great repost is better than many mediocre ones
- Add genuine value - your comment should make the original tweet more valuable
- Be respectful - quote tweets can be seen as endorsements or criticisms
- Stay on brand - maintain consistent voice across all reposts

EXAMPLE WORKFLOW FOR "pick from trending":
1. User: "pick one from trending topics"
2. You: Call auto_trending_repost() -> get result
3. You: Extract post_id = result['selected_post']['id'], comment = result['generated_comment']['text']
4. You: Call post_quote_tweet_tool(post_id, comment, dry_run=True)
5. You: Present both results to user showing what was selected and posting status

EXAMPLES OF GOOD REPOST COMMENTS

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
