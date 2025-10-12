"""
CMO Agent Tools - A2A Protocol Communication Layer
All inter-agent communication goes through these standardized tools
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


# ===== A2A PROTOCOL LAYER =====

def call_agent_via_a2a(
    agent_name: str,
    action: str,
    params: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Universal A2A protocol caller

    Args:
        agent_name: Target agent (post_agent, quote_agent, reply_agent, repost_agent)
        action: Action to perform
        params: Action-specific parameters
        context: Shared context (trends, history, etc.)

    Returns:
        Standardized A2A response
    """
    request = {
        "action": action,
        "params": params,
        "context": context or {},
        "caller": "cmo_agent",
        "timestamp": datetime.utcnow().isoformat()
    }

    print(f"[CMO_AGENT] A2A Call: {agent_name}.{action}")

    # Route to appropriate agent
    try:
        if agent_name == "post_agent":
            from post_agent.agent import execute as post_execute
            response = post_execute(request)

        elif agent_name == "quote_agent":
            from quote_agent.agent import execute as quote_execute
            response = quote_execute(request)

        elif agent_name == "reply_agent":
            from reply_agent.agent import execute as reply_execute
            response = reply_execute(request)

        elif agent_name == "repost_agent":
            from repost_agent.agent import execute as repost_execute
            response = repost_execute(request)

        else:
            response = {
                "status": "failed",
                "error": f"Unknown agent: {agent_name}",
                "metadata": {
                    "agent": "cmo_agent",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        print(f"[CMO_AGENT] A2A Response: {response.get('status')}")
        return response

    except Exception as e:
        print(f"[CMO_AGENT ERROR] A2A call failed: {e}")
        import traceback
        traceback.print_exc()

        return {
            "status": "failed",
            "error": str(e),
            "metadata": {
                "agent": "cmo_agent",
                "target_agent": agent_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


# ===== CONVENIENCE WRAPPERS FOR SPECIFIC AGENTS =====

def call_post_agent(
    tone: str = "witty",
    topic: str = "",
    context_json: str = "{}"
) -> str:
    """
    Convenience wrapper for post_agent

    Args:
        tone: Content tone (default: "witty")
        topic: Content topic (empty string means auto-discover from trends)
        context_json: JSON string with trending context data

    Returns:
        JSON string with response
    """
    # Parse context from JSON string
    import json as json_lib
    context = json_lib.loads(context_json) if context_json and context_json != "{}" else None

    response = call_agent_via_a2a(
        agent_name="post_agent",
        action="create_post",
        params={
            "topic": topic if topic else None,
            "tone": tone,
            "require_approval": False  # Always post immediately
        },
        context=context
    )

    return json.dumps(response, indent=2)


def call_quote_agent(
    strategy: str = "trending",
    topic: str = "",
    tweet_url: str = "",
    context_json: str = "{}"
) -> str:
    """
    Convenience wrapper for quote_agent

    Args:
        strategy: Quote tweet strategy (trending, topic, manual)
        topic: Topic to find tweets about (empty string if none)
        tweet_url: Specific tweet URL to quote (empty string if none)
        context_json: JSON string with trending context data

    Returns:
        JSON string with response
    """
    # Parse context from JSON string
    import json as json_lib
    context = json_lib.loads(context_json) if context_json and context_json != "{}" else None

    response = call_agent_via_a2a(
        agent_name="quote_agent",
        action="create_quote_tweet",
        params={
            "strategy": strategy,
            "topic": topic if topic else None,
            "tweet_url": tweet_url if tweet_url else None,
            "require_approval": False  # Always post immediately
        },
        context=context
    )

    return json.dumps(response, indent=2)


def call_reply_agent(
    tweet_url: str,
    strategy: str = "insightful",
    context_json: str = "{}"
) -> str:
    """
    Convenience wrapper for reply_agent

    Args:
        tweet_url: Tweet URL to reply to
        strategy: Reply strategy (insightful, helpful, engaging, supportive, informative)
        context_json: JSON string with trending context data

    Returns:
        JSON string with response
    """
    if not tweet_url:
        return json.dumps({
            "status": "failed",
            "error": "tweet_url is required for reply_agent"
        })

    # Parse context from JSON string
    import json as json_lib
    context = json_lib.loads(context_json) if context_json and context_json != "{}" else None

    response = call_agent_via_a2a(
        agent_name="reply_agent",
        action="create_reply",
        params={
            "tweet_url": tweet_url,
            "strategy": strategy,
            "require_approval": False  # Always post immediately
        },
        context=context
    )

    return json.dumps(response, indent=2)


def call_repost_agent(
    tweet_url: str,
    context_json: str = "{}"
) -> str:
    """
    Convenience wrapper for repost_agent

    Args:
        tweet_url: Tweet URL to repost
        context_json: JSON string with trending context data

    Returns:
        JSON string with response
    """
    if not tweet_url:
        return json.dumps({
            "status": "failed",
            "error": "tweet_url is required for repost_agent"
        })

    # Parse context from JSON string
    import json as json_lib
    context = json_lib.loads(context_json) if context_json and context_json != "{}" else None

    response = call_agent_via_a2a(
        agent_name="repost_agent",
        action="repost",
        params={
            "tweet_url": tweet_url,
            "require_approval": False  # Always post immediately
        },
        context=context
    )

    return json.dumps(response, indent=2)


def get_trending_context() -> str:
    """
    Get current trending topics and context from real trend_data/ directory

    Returns:
        JSON string with trending context
    """
    trend_data_dir = Path(__file__).parent.parent / "trend_data"

    if not trend_data_dir.exists():
        print("⚠️ trend_data/ directory not found, using fallback data")
        return _get_fallback_trending_context()

    # Find most recent trending_*.json file
    trend_files = sorted(trend_data_dir.glob("trending_*.json"), reverse=True)

    if not trend_files:
        print("⚠️ No trend data files found in trend_data/, using fallback")
        return _get_fallback_trending_context()

    latest_file = trend_files[0]
    print(f"📊 Loading trending context from: {latest_file.name}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            trend_data = json.load(f)

        trending_topics = []
        keywords = set()
        hashtags = set()

        data_sources = trend_data.get("data_sources", {})

        # Extract from Twitter trends
        if "twitter_trends" in data_sources:
            twitter_trends = data_sources["twitter_trends"]
            if twitter_trends.get("collected"):
                tabs_data = twitter_trends.get("data", {}).get("tabs", {})

                for category, tab_info in tabs_data.items():
                    topics_list = tab_info.get("trending_topics", [])

                    # Get top 5 topics from each category
                    for topic in topics_list[:5]:
                        topic_name = topic.get("topic_name", "")

                        # Extract hashtags
                        if "#" in topic_name:
                            words = topic_name.split()
                            for word in words:
                                if word.startswith("#"):
                                    hashtags.add(word.strip("#"))

                        # Calculate trend score based on rank
                        rank = topic.get("rank", 999)
                        trend_score = max(0.5, 1.0 - (rank / 100))

                        # Determine relevance based on engagement_hint
                        engagement = topic.get("engagement_hint", "unknown")
                        relevance = "high" if engagement == "high" else "medium" if engagement == "medium" else "unknown"

                        trending_topics.append({
                            "topic": topic_name,
                            "trend_score": round(trend_score, 2),
                            "relevance": relevance,
                            "source": f"Twitter/{category}",
                            "url": topic.get("url", ""),
                            "rank": rank
                        })

        # Extract from Google Trends
        if "google_trends" in data_sources:
            google_trends = data_sources["google_trends"]
            if google_trends.get("collected") and google_trends.get("data"):
                gt_data = google_trends.get("data", {})

                # Extract trending searches
                for trend_item in gt_data.get("trending_searches", [])[:5]:
                    trending_topics.append({
                        "topic": trend_item.get("title", ""),
                        "trend_score": 0.85,
                        "relevance": "high",
                        "source": "Google Trends",
                        "url": trend_item.get("url", "")
                    })

        # Extract from post analysis (keywords)
        if "post_analysis" in data_sources:
            post_analysis = data_sources["post_analysis"]
            if post_analysis.get("collected"):
                analysis_data = post_analysis.get("data", {})
                for keyword_data in analysis_data.get("keywords", [])[:10]:
                    keyword = keyword_data.get("keyword", "")
                    keywords.add(keyword)

        # Sort trending topics by trend_score and limit to top 10
        trending_topics.sort(key=lambda x: (x.get("trend_score", 0), -x.get("rank", 999)), reverse=True)
        trending_topics = trending_topics[:10]

        # Peak posting times (static recommendations based on research)
        peak_posting_times = [
            "09:00-11:00 PST",
            "15:00-17:00 PST",
            "19:00-21:00 PST"
        ]

        # Get recommended hashtags (prioritize from trends, then add generic defaults)
        recommended_hashtags = list(hashtags)[:8]
        default_hashtags = ["BuildInPublic", "TechTwitter", "Trending"]
        for tag in default_hashtags:
            if tag not in recommended_hashtags and len(recommended_hashtags) < 8:
                recommended_hashtags.append(tag)

        result = {
            "status": "success",
            "source": "trend_data",
            "trending_topics": trending_topics,
            "keywords": list(keywords)[:15],
            "peak_posting_times": peak_posting_times,
            "recommended_hashtags": recommended_hashtags,
            "data_timestamp": trend_data.get("pipeline_metadata", {}).get("pipeline_timestamp", ""),
            "timestamp": datetime.utcnow().isoformat()
        }

        print(f"✅ Loaded {len(trending_topics)} trending topics from real data")
        return json.dumps(result, indent=2)

    except Exception as e:
        print(f"❌ Error loading trending context: {e}")
        import traceback
        traceback.print_exc()
        return _get_fallback_trending_context()


def _get_fallback_trending_context() -> str:
    """Fallback trending context when real data is unavailable"""
    trends = {
        "status": "fallback",
        "source": "no_trend_data_available",
        "message": "No trend data found. Run trend_research_pipeline to collect real trends.",
        "trending_topics": [],
        "keywords": [],
        "peak_posting_times": [
            "09:00-11:00 PST",
            "15:00-17:00 PST",
            "19:00-21:00 PST"
        ],
        "recommended_hashtags": ["BuildInPublic", "TechTwitter"],
        "timestamp": datetime.utcnow().isoformat()
    }

    return json.dumps(trends, indent=2)
