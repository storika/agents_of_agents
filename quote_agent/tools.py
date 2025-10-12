"""
X (Twitter) API Tools
Tools for searching posts and creating quote tweets with LLM-generated comments
"""

import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

import google.generativeai as genai
import weave
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ["WANDB_API_KEY"] = WANDB_API_KEY
WEAVE_PROJECT = os.getenv("WEAVE_PROJECT", "your-org/your-project")
weave.init(WEAVE_PROJECT)

# Initialize Gemini for LLM
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Twitter API
try:
    from pytwitter import Api

    # Use OAuth 2.0 for write operations (same as post_agent)
    TW_OAUTH2_ACCESS_TOKEN = os.getenv("TW_OAUTH2_ACCESS_TOKEN")

    if TW_OAUTH2_ACCESS_TOKEN:
        twitter_api = Api(bearer_token=TW_OAUTH2_ACCESS_TOKEN)
        print("✅ Twitter API initialized with OAuth 2.0 (TW_OAUTH2_ACCESS_TOKEN)")
    else:
        twitter_api = None
        print("⚠️ Twitter API credentials not found in .env - will use mock mode")
        print("   Required: TW_OAUTH2_ACCESS_TOKEN")

except ImportError:
    twitter_api = None
    print("⚠️ pytwitter not installed - will use mock mode")
    print("   Install with: uv pip install python-twitter-v2")


def load_trending_posts_from_data(max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Load trending posts from the most recent trend_data/ file

    Returns:
        List of trending post dictionaries with url, text, engagement info
    """
    trend_data_dir = Path(__file__).parent.parent / "trend_data"

    if not trend_data_dir.exists():
        print("⚠️ trend_data/ directory not found")
        return []

    # Find most recent trending_*.json file
    trend_files = sorted(trend_data_dir.glob("trending_*.json"), reverse=True)

    if not trend_files:
        print("⚠️ No trend data files found in trend_data/")
        return []

    latest_file = trend_files[0]
    print(f"📊 Loading trending posts from: {latest_file.name}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            trend_data = json.load(f)

        posts = []
        data_sources = trend_data.get("data_sources", {})

        # Extract from twitter_trends
        if "twitter_trends" in data_sources:
            twitter_trends = data_sources["twitter_trends"]
            if twitter_trends.get("collected"):
                tabs_data = twitter_trends.get("data", {}).get("tabs", {})

                for category, tab_info in tabs_data.items():
                    topics_list = tab_info.get("trending_topics", [])
                    for topic in topics_list[:max_results]:
                        url = topic.get("url", "")

                        # Skip search URLs - only include actual tweet URLs (with /status/)
                        if "/search?" in url or not "/status/" in url:
                            continue

                        posts.append({
                            "id": url.split("/status/")[1].split("?")[0] if "/status/" in url else f"trend_{topic.get('rank', 0)}",
                            "text": topic.get("raw_text", topic.get("topic_name", ""))[:280],
                            "author_id": "trending_user",
                            "created_at": topic.get("timestamp", ""),
                            "metrics": {
                                "likes": 150 + (topic.get("rank", 10) * 10),  # Estimated
                                "retweets": 75 + (topic.get("rank", 10) * 5),  # Estimated
                                "replies": 30 + (topic.get("rank", 10) * 2),  # Estimated
                            },
                            "url": url,
                            "source": f"trend_data/{category}",
                            "engagement_hint": topic.get("engagement_hint", "unknown")
                        })

        # Extract from post_analysis with actual post content
        if "post_analysis" in data_sources:
            post_analysis_data = data_sources["post_analysis"]
            if post_analysis_data.get("collected"):
                analysis_data = post_analysis_data.get("data", {})
                for keyword_data in analysis_data.get("keywords", [])[:max_results]:
                    keyword = keyword_data.get("keyword", "")
                    posts_list = keyword_data.get("posts", [])

                    for post in posts_list[:3]:  # Top 3 posts per keyword
                        posts.append({
                            "id": post.get("url", "").split("/")[-1] if "/" in post.get("url", "") else f"post_{len(posts)}",
                            "text": post.get("content", post.get("title", ""))[:280],
                            "author_id": "analyzed_user",
                            "created_at": post.get("published_date", ""),
                            "metrics": {
                                "likes": post.get("score", 50),
                                "retweets": post.get("score", 50) // 2,
                                "replies": post.get("score", 50) // 5,
                            },
                            "url": post.get("url", ""),
                            "source": f"post_analysis/{keyword}",
                            "keyword": keyword
                        })

        posts = posts[:max_results]
        print(f"✅ Loaded {len(posts)} trending posts from data")
        return posts

    except Exception as e:
        print(f"❌ Error loading trending posts: {e}")
        return []


@weave.op()
def search_recent_posts(
    query: str, max_results: int = 10, tweet_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for recent posts on X/Twitter based on a query

    Args:
        query: Search query (e.g., "AI agents", "#BuildInPublic", "from:username")
        max_results: Maximum number of results to return (5-100, default: 10)
        tweet_fields: Additional tweet fields to return

    Returns:
        Dictionary with search results
    """

    print(f"🔍 Searching X for: '{query}' (max: {max_results})")

    if tweet_fields is None:
        tweet_fields = ["created_at", "author_id", "public_metrics", "conversation_id"]

    try:
        if twitter_api:
            # Try real API call
            try:
                response = twitter_api.search_tweets(
                    query=query,
                    max_results=min(max_results, 100),  # API limit
                    tweet_fields=tweet_fields,
                )

                posts = []
                if response.data:
                    for tweet in response.data:
                        posts.append(
                            {
                                "id": tweet.id,
                                "text": tweet.text,
                                "author_id": tweet.author_id
                                if hasattr(tweet, "author_id")
                                else None,
                                "created_at": tweet.created_at
                                if hasattr(tweet, "created_at")
                                else None,
                                "metrics": {
                                    "likes": tweet.public_metrics.get("like_count", 0)
                                    if hasattr(tweet, "public_metrics")
                                    else 0,
                                    "retweets": tweet.public_metrics.get(
                                        "retweet_count", 0
                                    )
                                    if hasattr(tweet, "public_metrics")
                                    else 0,
                                    "replies": tweet.public_metrics.get(
                                        "reply_count", 0
                                    )
                                    if hasattr(tweet, "public_metrics")
                                    else 0,
                                }
                                if hasattr(tweet, "public_metrics")
                                else {},
                                "url": f"https://twitter.com/i/web/status/{tweet.id}",
                            }
                        )

                result = {
                    "status": "success",
                    "query": query,
                    "total_results": len(posts),
                    "posts": posts,
                }

                print(f"✅ Found {len(posts)} real posts from X API")
                return result

            except Exception as api_error:
                # Auth error - fall back to trending data
                print("⚠️ X API auth error - using trending data instead")
                print(f"   Error: {str(api_error)[:100]}")
                # Fall through to trending data mode below

        # Try to load from trending data first
        print("⚠️ Using trending data from trend_data/")
        posts = load_trending_posts_from_data(max_results=max_results)

        if posts:
            result = {
                "status": "trending_data",
                "query": query,
                "total_results": len(posts),
                "posts": posts,
                "source": "trend_data directory (real-time collection)"
            }
        else:
            # Ultimate fallback - mock data
            print("⚠️ No trending data available, using mock data")
            posts = [
                {
                    "id": "1234567890",
                    "text": f"Just shipped multi-agent systems in production! The debugging complexity is real but velocity gains are worth it. Query: {query}",
                    "author_id": "9876543210",
                    "created_at": "2025-10-11T10:30:00Z",
                    "metrics": {"likes": 342, "retweets": 87, "replies": 45},
                    "url": "https://twitter.com/i/web/status/1234567890",
                },
                {
                    "id": "1234567891",
                    "text": f"Unpopular opinion: Most teams don't need {query}. Start simple, scale when you have proof.",
                    "author_id": "9876543211",
                    "created_at": "2025-10-11T09:15:00Z",
                    "metrics": {"likes": 156, "retweets": 34, "replies": 89},
                    "url": "https://twitter.com/i/web/status/1234567891",
                },
                {
                    "id": "1234567892",
                    "text": f"The hardest part about {query} isn't the tech - it's the orchestration and debugging. Infrastructure is 80% of work.",
                    "author_id": "9876543212",
                    "created_at": "2025-10-11T08:45:00Z",
                    "metrics": {"likes": 523, "retweets": 142, "replies": 67},
                    "url": "https://twitter.com/i/web/status/1234567892",
                },
            ]

            result = {
                "status": "mock",
                "query": query,
                "total_results": min(max_results, len(posts)),
                "posts": posts[:max_results],
            }

        return result

    except Exception as e:
        print(f"❌ Error searching posts: {e}")
        return {
            "status": "error",
            "error": str(e),
            "query": query,
            "total_results": 0,
            "posts": [],
        }


@weave.op()
def generate_quote_tweet_comment(
    post_text: str, context: Optional[str] = None, max_length: int = 200
) -> str:
    """
    Generate a short, relevant comment for quote tweeting using LLM

    Args:
        post_text: The original post text to quote
        context: Additional context about the post (optional)
        max_length: Maximum character length (default: 200)

    Returns:
        Generated comment text
    """

    print(f"✍️ Generating quote tweet comment...")

    system_prompt = f"""You are a quote tweet comment generator for X/Twitter. Generate ONE short, engaging comment that adds value to the original post.

AUDIENCE: AI/ML developers, indie hackers, founders, tech community
TONE: Conversational, witty-but-respectful, builder-friendly
STYLE: Authentic, adds perspective or insight

STRATEGIES (pick the most suitable):
- EXPERIENCE: Share a brief personal/team experience
- QUESTION: Ask a thoughtful, specific question
- ANALYSIS: Add a quick technical insight
- REACTION: Express genuine reaction with added value

RULES:
- MUST be ≤{max_length} characters
- Add meaningful value - never just "This!" or "Great post!"
- Be specific and concrete
- Use natural language
- Max 1 emoji if natural
- Make it standalone - should work even without seeing the original

OUTPUT: Return ONLY the comment text, nothing else. No quotes, no explanations."""

    user_prompt = f"""Original Post:
"{post_text}"
"""

    if context:
        user_prompt += f"\nContext: {context}\n"

    user_prompt += f"\nGenerate a {max_length}-char comment that adds unique value:"

    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
        comment = response.text.strip()

        # Remove quotes if present
        if comment.startswith('"') and comment.endswith('"'):
            comment = comment[1:-1]
        if comment.startswith("'") and comment.endswith("'"):
            comment = comment[1:-1]

        # Truncate if too long
        if len(comment) > max_length:
            comment = comment[: max_length - 3] + "..."

        print(f"✅ Generated: {comment[:60]}...")
        return comment

    except Exception as e:
        print(f"❌ Error generating comment: {e}")
        return "Interesting perspective! Would love to hear more about your experience with this."


@weave.op()
def quote_tweet_post(
    post_id: str, comment: str, dry_run: bool = True
) -> Dict[str, Any]:
    """
    Create a quote tweet (repost with comment) on X/Twitter

    Args:
        post_id: ID of the post to quote tweet
        comment: Your comment text
        dry_run: If True, don't actually post (default: True)

    Returns:
        Result dictionary with status
    """

    print(f"{'[DRY RUN] ' if dry_run else ''}📤 Quote tweeting post {post_id}")

    if len(comment) > 280:
        return {
            "status": "error",
            "error": f"Comment too long: {len(comment)} chars (max: 280)",
        }

    try:
        if dry_run:
            result = {
                "status": "dry_run_success",
                "message": "Quote tweet would be posted (dry run mode)",
                "post_id": post_id,
                "comment": comment,
                "character_count": len(comment),
                "note": "Set dry_run=False to actually post",
            }
            print(f"✅ Dry run successful")
            return result

        if twitter_api:
            # Real API call - Note: python-twitter uses quote_tweet_id parameter
            response = twitter_api.create_tweet(text=comment, quote_tweet_id=post_id)

            if response and response.data:
                result = {
                    "status": "success",
                    "message": "Quote tweet posted successfully",
                    "tweet_id": response.data.id,
                    "quoted_post_id": post_id,
                    "comment": comment,
                    "url": f"https://twitter.com/i/web/status/{response.data.id}",
                }
                print(f"✅ Posted successfully: {result['url']}")
                return result
            else:
                return {
                    "status": "error",
                    "error": "Failed to create tweet - no response data",
                }
        else:
            return {
                "status": "error",
                "error": "Twitter API not configured - check credentials in .env",
            }

    except Exception as e:
        print(f"❌ Error posting quote tweet: {e}")
        return {"status": "error", "error": str(e), "post_id": post_id}


@weave.op()
def quote_to_x(
    tweet_url: str,
    comment: str,
    actually_post: bool = True,
    require_approval: bool = False
) -> str:
    """
    Publish quote tweet to Twitter/X (similar to post_to_x for regular posts)

    Args:
        tweet_url: URL of the tweet to quote
        comment: Your comment text for the quote tweet
        actually_post: If True, actually post; if False, simulate (default: True - always post)
        require_approval: If True, queue for approval (default: False - no approval needed)

    Returns:
        JSON string with posting status

    Workflow:
        1. Extract tweet ID from URL
        2. Validate comment length
        3. Post quote tweet with comment
    """
    from datetime import datetime

    # Extract tweet ID from URL
    # URLs like: https://twitter.com/user/status/123456 or https://x.com/user/status/123456
    tweet_id = None
    if "/status/" in tweet_url:
        tweet_id = tweet_url.split("/status/")[1].split("?")[0].split("/")[0]
    else:
        result = {
            "status": "failed",
            "error": "Invalid tweet URL - cannot extract tweet ID",
            "tweet_url": tweet_url,
            "message": "❌ 올바른 트윗 URL이 아닙니다."
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    # If approval required, queue only
    if require_approval:
        result = {
            "status": "queued",
            "quote_id": f"queued_{datetime.now().timestamp()}",
            "tweet_url": tweet_url,
            "tweet_id": tweet_id,
            "comment": comment,
            "scheduled_time": datetime.now().isoformat(),
            "requires_approval": True,
            "message": "승인 대기 중입니다."
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    # Validate comment length
    if len(comment) > 280:
        result = {
            "status": "failed",
            "error": f"Comment too long: {len(comment)} chars (max: 280)",
            "comment": comment,
            "message": f"❌ 댓글이 너무 깁니다 ({len(comment)}/280자)"
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    # Actually post
    if actually_post:
        print(f"[INFO] ==========================================")
        print(f"[INFO] 인용 트윗 발행 중...")
        print(f"[INFO] 원본 트윗: {tweet_url}")
        print(f"[INFO] 댓글: {comment[:50]}{'...' if len(comment) > 50 else ''}")
        print(f"[INFO] ==========================================")

        try:
            if twitter_api:
                # Real API call
                response = twitter_api.create_tweet(text=comment, quote_tweet_id=tweet_id)

                # Handle both Response.data and direct Tweet object
                tweet_data = None
                if response:
                    if hasattr(response, 'data') and response.data:
                        tweet_data = response.data
                    elif hasattr(response, 'id'):
                        # Direct Tweet object
                        tweet_data = response

                if tweet_data and hasattr(tweet_data, 'id'):
                    result = {
                        "status": "published",
                        "quote_id": tweet_data.id,
                        "tweet_url": tweet_url,
                        "quoted_tweet_id": tweet_id,
                        "comment": comment,
                        "character_count": len(comment),
                        "published_time": datetime.now().isoformat(),
                        "message": "✅ 성공적으로 X에 인용 트윗이 발행되었습니다!",
                        "url": f"https://twitter.com/i/web/status/{tweet_data.id}"
                    }
                    print(f"[INFO] ✅ 성공: {result['url']}")
                else:
                    result = {
                        "status": "failed",
                        "error": "Failed to create quote tweet - no response data",
                        "tweet_url": tweet_url,
                        "comment": comment,
                        "message": "❌ 트윗 생성 실패 - 응답 데이터 없음"
                    }
                    print(f"[ERROR] ❌ 실패: 응답 데이터 없음")
            else:
                # No API configured - simulation mode
                result = {
                    "status": "simulated",
                    "quote_id": f"sim_{datetime.now().timestamp()}",
                    "tweet_url": tweet_url,
                    "quoted_tweet_id": tweet_id,
                    "comment": comment,
                    "message": "⚠️ Twitter API가 설정되지 않아 시뮬레이션 모드로 처리되었습니다.",
                    "note": "실제로 포스팅하려면 .env에 Twitter 자격증명을 설정하세요"
                }
                print(f"[WARN] ⚠️ API 미설정 - 시뮬레이션 모드")

        except Exception as e:
            result = {
                "status": "failed",
                "error": str(e),
                "tweet_url": tweet_url,
                "comment": comment,
                "message": f"❌ 인용 트윗 발행 실패: {str(e)}"
            }
            print(f"[ERROR] ❌ 예외 발생: {e}")
    else:
        # Simulation mode
        result = {
            "status": "simulated",
            "quote_id": f"sim_{datetime.now().timestamp()}",
            "tweet_url": tweet_url,
            "quoted_tweet_id": tweet_id,
            "comment": comment,
            "scheduled_time": datetime.now().isoformat(),
            "message": "시뮬레이션: 실제로는 X에 발행되지 않았습니다."
        }

    return json.dumps(result, indent=2, ensure_ascii=False)


@weave.op()
def auto_repost_workflow(
    query: str,
    max_search_results: int = 10,
    auto_select: bool = True,
    comment_max_length: int = 200,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Complete automated workflow: search posts, pick one, generate comment, quote tweet

    Args:
        query: Search query for posts
        max_search_results: Max posts to fetch
        auto_select: If True, auto-select top post by engagement
        comment_max_length: Max length for generated comment
        dry_run: If True, don't actually post

    Returns:
        Complete workflow result
    """

    print("\n" + "=" * 70)
    print("🤖 AUTO-REPOST WORKFLOW")
    print("=" * 70)

    # Step 1: Search posts
    print("\n📍 Step 1: Searching for posts...")
    search_result = search_recent_posts(query, max_results=max_search_results)

    if search_result["status"] == "error" or not search_result["posts"]:
        return {
            "status": "error",
            "step": "search",
            "error": "No posts found or search failed",
        }

    # Step 2: Select a post
    print("\n📍 Step 2: Selecting post...")

    if auto_select:
        # Select post with highest engagement
        posts = search_result["posts"]
        selected_post = max(
            posts,
            key=lambda p: p.get("metrics", {}).get("likes", 0)
            + p.get("metrics", {}).get("retweets", 0) * 2,
        )
        print(f"   Auto-selected top post by engagement")
    else:
        selected_post = search_result["posts"][0]
        print(f"   Selected first post")

    print(f"   Post: {selected_post['text'][:80]}...")
    print(
        f"   Engagement: {selected_post.get('metrics', {}).get('likes', 0)} likes, "
        f"{selected_post.get('metrics', {}).get('retweets', 0)} retweets"
    )

    # Step 3: Generate comment
    print("\n📍 Step 3: Generating comment with LLM...")
    comment = generate_quote_tweet_comment(
        post_text=selected_post["text"],
        context=f"This post has {selected_post.get('metrics', {}).get('likes', 0)} likes",
        max_length=comment_max_length,
    )

    print(f"   Generated: {comment}")

    # Step 4: Quote tweet
    print(f"\n📍 Step 4: {'[DRY RUN] ' if dry_run else ''}Quote tweeting...")
    quote_result = quote_tweet_post(
        post_id=selected_post["id"], comment=comment, dry_run=dry_run
    )

    # Final result
    result = {
        "status": "success"
        if quote_result["status"] in ["success", "dry_run_success"]
        else "error",
        "workflow_steps": {
            "search": {"query": query, "total_found": search_result["total_results"]},
            "selected_post": {
                "id": selected_post["id"],
                "text": selected_post["text"],
                "url": selected_post["url"],
                "metrics": selected_post.get("metrics", {}),
            },
            "generated_comment": {"text": comment, "length": len(comment)},
            "quote_tweet": quote_result,
        },
    }

    print("\n" + "=" * 70)
    if quote_result["status"] in ["success", "dry_run_success"]:
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        if dry_run:
            print("   (Dry run mode - nothing was actually posted)")
    else:
        print("❌ WORKFLOW FAILED")
    print("=" * 70 + "\n")

    return result


# Helper function for pretty printing workflow results
def print_workflow_result(result: Dict[str, Any]) -> None:
    """Pretty print workflow result"""

    if result["status"] == "error":
        print(f"❌ Workflow failed at step: {result.get('step', 'unknown')}")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return

    steps = result["workflow_steps"]

    print("\n📊 WORKFLOW SUMMARY")
    print("=" * 70)

    print(f"\n🔍 Search:")
    print(f"   Query: {steps['search']['query']}")
    print(f"   Found: {steps['search']['total_found']} posts")

    print(f"\n🎯 Selected Post:")
    print(f"   Text: {steps['selected_post']['text'][:100]}...")
    print(f"   URL: {steps['selected_post']['url']}")
    metrics = steps["selected_post"]["metrics"]
    print(
        f"   Engagement: {metrics.get('likes', 0)} likes, "
        f"{metrics.get('retweets', 0)} retweets, {metrics.get('replies', 0)} replies"
    )

    print(f"\n✍️ Generated Comment:")
    print(f"   {steps['generated_comment']['text']}")
    print(f"   Length: {steps['generated_comment']['length']}/280 chars")

    print(f"\n📤 Quote Tweet Status:")
    qt = steps["quote_tweet"]
    print(f"   Status: {qt['status']}")
    if qt["status"] == "success":
        print(f"   URL: {qt.get('url', 'N/A')}")
    elif qt["status"] == "dry_run_success":
        print(f"   Note: {qt.get('note', 'Dry run')}")

    print("=" * 70)


# ===== AUTO TRENDING REPOST =====

@weave.op()
def auto_trending_repost(max_results: int = 10) -> Dict[str, Any]:
    """
    Automatically select a random trending post and generate a repost with comment

    Returns:
        Complete repost workflow result with selected post and generated comment
    """
    import random

    print("\n" + "="*70)
    print("🤖 AUTO TRENDING REPOST")
    print("="*70)

    # Load trending posts
    print("\n📍 Loading trending posts...")
    posts = load_trending_posts_from_data(max_results=max_results)

    if not posts:
        return {
            "status": "error",
            "error": "No trending posts available. Please run trend_research_pipeline first."
        }

    # Randomly select one post
    selected_post = random.choice(posts)
    print(f"🎲 Randomly selected post: {selected_post['text'][:80]}...")
    print(f"   URL: {selected_post['url']}")
    print(f"   Source: {selected_post.get('source', 'N/A')}")

    # Generate comment for the selected post
    print("\n📍 Generating comment with LLM...")
    comment = generate_quote_tweet_comment(
        post_text=selected_post["text"],
        context=f"Trending post with {selected_post.get('metrics', {}).get('likes', 0)} likes",
        max_length=200
    )

    print(f"   Generated: {comment}")

    # Return result (not actually posting)
    result = {
        "status": "ready",
        "message": "Ready to post (set dry_run=False to actually post)",
        "selected_post": {
            "id": selected_post["id"],
            "text": selected_post["text"],
            "url": selected_post["url"],
            "source": selected_post.get("source", "N/A"),
            "metrics": selected_post.get("metrics", {})
        },
        "generated_comment": {
            "text": comment,
            "length": len(comment)
        },
        "preview": f"{comment}\n\n[Quoting: {selected_post['text'][:100]}...]"
    }

    print("\n" + "="*70)
    print("✅ TRENDING REPOST READY")
    print("="*70)
    print(f"\nComment: {comment}")
    print(f"Quoting: {selected_post['url']}")
    print(f"\nTo post: call quote_tweet_post('{selected_post['id']}', '{comment}', dry_run=False)")
    print("="*70 + "\n")

    return result


# ===== LEGACY WRAPPER FUNCTIONS FOR BACKWARD COMPATIBILITY =====
# These are for compatibility with repost_agent/agent.py that uses old function names


@weave.op()
def find_trending_tweets_tool(topic: str, max_results: int = 10) -> str:
    """Legacy wrapper for search_recent_posts - returns JSON string"""
    result = search_recent_posts(query=topic, max_results=max_results)

    # Convert to old format expected by agent.py
    tweets = []
    for post in result.get("posts", []):
        tweets.append(
            {
                "text": post["text"],
                "url": post["url"],
                "author": f"@user{post['author_id']}"
                if post.get("author_id")
                else "@unknown",
                "engagement": post.get("metrics", {}).get("likes", 0),
            }
        )

    return json.dumps(
        {"status": result["status"], "topic": topic, "tweets": tweets}, indent=2
    )


@weave.op()
def generate_repost_comment_tool(
    tweet_text: str, author: str = "@unknown", strategy: str = "auto"
) -> str:
    """
    Legacy wrapper - generates multiple scored comment options
    Returns JSON string with comment options and scores
    """

    strategies = [
        "experience",
        "question",
        "analysis",
        "reaction",
        "context",
        "connect",
    ]
    if strategy == "auto":
        import random

        strategy = random.choice(strategies)

    # Generate primary comment
    primary_comment = generate_quote_tweet_comment(
        post_text=tweet_text,
        context=f"Author: {author}, Strategy: {strategy}",
        max_length=180,
    )

    # Generate 2 alternative comments with different strategies
    alt_strategies = [s for s in strategies if s != strategy][:2]
    alt_comments = []

    for alt_strategy in alt_strategies:
        alt_comment = generate_quote_tweet_comment(
            post_text=tweet_text,
            context=f"Author: {author}, Strategy: {alt_strategy}",
            max_length=180,
        )
        alt_comments.append((alt_strategy, alt_comment))

    # Build scored results (mock scoring)
    import random

    def score_comment(text, strat):
        base = 0.75
        return {
            "comment": text,
            "strategy": strat,
            "character_count": len(text),
            "scores": {
                "value_add": round(base + random.uniform(0, 0.2), 2),
                "engagement_potential": round(base + random.uniform(0, 0.25), 2),
                "authenticity": round(base + random.uniform(0, 0.2), 2),
                "safety": round(0.95 + random.uniform(0, 0.05), 2),
                "overall": round(base + random.uniform(0.1, 0.25), 2),
            },
            "reasoning": f"Using {strat} strategy - adds value through relevant perspective",
        }

    comments = [score_comment(primary_comment, strategy)]
    for alt_strat, alt_comm in alt_comments:
        comments.append(score_comment(alt_comm, alt_strat))

    # Sort by overall score
    comments.sort(key=lambda c: c["scores"]["overall"], reverse=True)

    return json.dumps(
        {
            "status": "success",
            "tweet_text": tweet_text,
            "author": author,
            "generated_comments": comments,
        },
        indent=2,
    )


@weave.op()
def post_quote_tweet_tool(
    original_tweet_url: str, comment: str, dry_run: bool = True
) -> str:
    """Legacy wrapper for quote_tweet_post - returns JSON string"""

    # Extract post ID from URL
    post_id = (
        original_tweet_url.split("/")[-1]
        if "/" in original_tweet_url
        else original_tweet_url
    )

    result = quote_tweet_post(post_id=post_id, comment=comment, dry_run=dry_run)

    return json.dumps(result, indent=2)


@weave.op()
def analyze_tweet_for_repost(tweet_text: str, author: str = "@unknown") -> str:
    """
    Analyze a tweet and recommend the best repost strategy
    Returns JSON string with analysis
    """

    # Simple keyword-based strategy recommendation
    text_lower = tweet_text.lower()

    if any(
        word in text_lower
        for word in ["shipped", "built", "made", "created", "launched"]
    ):
        strategy = "experience"
        reason = "Tweet discusses building/shipping - share your experience"
    elif any(word in text_lower for word in ["?", "how", "why", "what", "when"]):
        strategy = "question"
        reason = "Tweet asks question - respond with thoughtful question"
    elif any(word in text_lower for word in ["future", "trend", "believe", "think"]):
        strategy = "analysis"
        reason = "Tweet discusses trends/future - add technical analysis"
    elif any(word in text_lower for word in ["amazing", "wow", "incredible", "love"]):
        strategy = "reaction"
        reason = "Tweet shows excitement - express genuine reaction with value"
    else:
        strategy = "context"
        reason = "General tweet - add helpful context or background"

    return json.dumps(
        {
            "tweet_text": tweet_text,
            "author": author,
            "recommended_strategy": strategy,
            "reasoning": reason,
            "alternative_strategies": ["experience", "question", "analysis"],
        },
        indent=2,
    )


if __name__ == "__main__":
    # Example usage
    print("\n🚀 X API Tools - Example Usage\n")

    # Example 1: Search posts
    print("Example 1: Search for posts")
    print("-" * 50)
    result = search_recent_posts("AI agents", max_results=5)
    print(f"Found {result['total_results']} posts\n")

    # Example 2: Generate comment
    print("\nExample 2: Generate comment for a post")
    print("-" * 50)
    if result["posts"]:
        post = result["posts"][0]
        comment = generate_quote_tweet_comment(post["text"])
        print(f"Comment: {comment}\n")

    # Example 3: Full workflow
    print("\nExample 3: Full auto-repost workflow (dry run)")
    print("-" * 50)
    workflow_result = auto_repost_workflow(
        query="multi-agent systems", max_search_results=5, dry_run=True
    )
    print_workflow_result(workflow_result)
