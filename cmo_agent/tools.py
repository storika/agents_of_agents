"""
CMO Agent Tools - A2A Protocol Communication Layer
All inter-agent communication goes through these standardized tools
"""

import json
import os
import re
import time
import weave
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from apify_client import ApifyClient
from weave.trace_server.trace_server_interface import CallsFilter


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
    context_json: str = "{}",
    media_type: str = "image"
) -> str:
    """
    Convenience wrapper for post_agent
    
    Args:
        tone: Content tone (default: "witty")
        topic: Content topic (empty string means auto-discover from trends)
        context_json: JSON string with trending context data
        media_type: Type of media to generate - "image" or "video" (default: "image")
    
    Returns:
        JSON string with response
    """
    # Parse context from JSON string - safe version
    import json as json_lib
    context = None
    if context_json and context_json != "{}":
        try:
            # Limit size
            if len(context_json) > 50000:
                print(f"[WARNING] context_json too large ({len(context_json)} chars) in call_post_agent")
                context_json = context_json[:50000]
            context = json_lib.loads(context_json)
        except json_lib.JSONDecodeError as e:
            print(f"[WARNING] Failed to parse context_json in call_post_agent: {e}")
            context = None

    response = call_agent_via_a2a(
        agent_name="post_agent",
        action="create_post",
        params={
            "topic": topic if topic else None,
            "tone": tone,
            "media_type": media_type,  # Pass media type to post_agent
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
    # Parse context from JSON string - safe version
    import json as json_lib
    context = None
    if context_json and context_json != "{}":
        try:
            # Limit size
            if len(context_json) > 50000:
                print(f"[WARNING] context_json too large ({len(context_json)} chars) in call_quote_agent")
                context_json = context_json[:50000]
            context = json_lib.loads(context_json)
        except json_lib.JSONDecodeError as e:
            print(f"[WARNING] Failed to parse context_json in call_quote_agent: {e}")
            context = None

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

    # Parse context from JSON string - safe version
    import json as json_lib
    context = None
    if context_json and context_json != "{}":
        try:
            # Limit size
            if len(context_json) > 50000:
                print(f"[WARNING] context_json too large ({len(context_json)} chars) in call_reply_agent")
                context_json = context_json[:50000]
            context = json_lib.loads(context_json)
        except json_lib.JSONDecodeError as e:
            print(f"[WARNING] Failed to parse context_json in call_reply_agent: {e}")
            context = None

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

    # Parse context from JSON string - safe version
    import json as json_lib
    context = None
    if context_json and context_json != "{}":
        try:
            # Limit size
            if len(context_json) > 50000:
                print(f"[WARNING] context_json too large ({len(context_json)} chars) in call_repost_agent")
                context_json = context_json[:50000]
            context = json_lib.loads(context_json)
        except json_lib.JSONDecodeError as e:
            print(f"[WARNING] Failed to parse context_json in call_repost_agent: {e}")
            context = None

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

                    # Get top 10 topics from each category (Twitter has ~20 per tab)
                    for topic in topics_list[:10]:
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
                gt_data = google_trends.get("data", [])
                
                # Handle both list and dict formats
                if isinstance(gt_data, list):
                    # Data is directly a list of trends
                    for trend_item in gt_data[:10]:
                        topic = trend_item.get("Trends") or trend_item.get("title", "")
                        if topic:
                            trending_topics.append({
                                "topic": topic,
                                "trend_score": 0.85,
                                "relevance": "high",
                                "source": "Google Trends",
                                "search_volume": trend_item.get("Search volume", ""),
                                "url": trend_item.get("Explore link") or trend_item.get("url", "")
                            })
                elif isinstance(gt_data, dict):
                    # Data has nested structure with trending_searches
                    for trend_item in gt_data.get("trending_searches", [])[:10]:
                        trending_topics.append({
                            "topic": trend_item.get("title", ""),
                            "trend_score": 0.85,
                            "relevance": "high",
                            "source": "Google Trends",
                            "url": trend_item.get("url", "")
                        })

        # Extract from trending posts analysis (keywords)
        if "trending_posts" in data_sources:
            trending_posts = data_sources["trending_posts"]
            if trending_posts.get("collected"):
                analysis_data = trending_posts.get("data", {})
                # Extract keywords from results
                for result_item in analysis_data.get("results", [])[:15]:
                    keyword = result_item.get("keyword", "")
                    if keyword:
                        keywords.add(keyword)

                # Also get summary keywords if available
                summary = analysis_data.get("summary", {})
                for summary_keyword in summary.get("keywords", [])[:10]:
                    keywords.add(summary_keyword)

        # Sort trending topics by trend_score and limit to top 15
        trending_topics.sort(key=lambda x: (x.get("trend_score", 0), -x.get("rank", 999)), reverse=True)
        trending_topics = trending_topics[:15]

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


def get_recent_performance_data(
    limit: int = 20,
    filter_op_name: Optional[str] = None
) -> str:
    """
    Weave에서 최근 실행 기록을 가져와서 성능 분석용 JSON으로 반환
    
    Args:
        limit: 가져올 call 개수 (기본: 20)
        filter_op_name: 특정 operation만 필터링 (예: "call_post_agent")
    
    Returns:
        JSON string with call performance data (costs/feedback 제외)
    """
    try:
        # Use existing Weave client
        client = weave.init(os.getenv("WANDB_PROJECT_ID", "mason-choi-storika/WeaveHacks2"))
        
        # Build filter using CallsFilter
        filter_arg = None
        if filter_op_name:
            filter_arg = CallsFilter(op_names=[filter_op_name])
        
        # Get calls with minimal columns (output only, no costs/feedback)
        calls_iter = client.get_calls(
            limit=limit,
            filter=filter_arg,
            include_costs=False,  # 비용 정보 제외
            include_feedback=False,  # 피드백 정보 제외
            columns=["output"],
            sort_by=[{"field": "started_at", "direction": "desc"}]
        )
        
        calls = list(calls_iter)
        print(f"[CMO_TOOLS] Found {len(calls)} recent calls")
        
        # Convert to JSON-serializable format
        calls_data = []
        for call in calls:
            call_dict = {
                "id": call.id,
                "trace_id": call.trace_id,
                "op_name": call.op_name,
                "started_at": call.started_at.isoformat() if call.started_at else None,
                "ended_at": call.ended_at.isoformat() if call.ended_at else None,
                "output": call.output if hasattr(call, 'output') else None,
                "exception": call.exception if hasattr(call, 'exception') else None,
                "success": call.exception is None
            }
            
            # Calculate execution time
            if call.started_at and call.ended_at:
                duration = (call.ended_at - call.started_at).total_seconds() * 1000
                call_dict["execution_time_ms"] = round(duration, 2)
            
            calls_data.append(call_dict)
        
        result = {
            "status": "success",
            "total_calls": len(calls_data),
            "filter": filter_op_name if filter_op_name else "all",
            "calls": calls_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return json.dumps(result, indent=2, default=str)
        
    except Exception as e:
        print(f"[CMO_TOOLS ERROR] Failed to get performance data: {e}")
        import traceback
        traceback.print_exc()
        
        return json.dumps({
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)


def measure_tweet_engagement(
    twitter_handle: str = "Mason_Storika",
    max_wait_minutes: int = 30
) -> str:
    """
    Measure engagement of past posts/quotes/reposts using Apify Tweet Scraper.

    This tool uses caching to avoid unnecessary API calls:
    - Checks for recent cached data (< 1 hour old)
    - Returns cached data if available
    - Otherwise, launches new Apify job and caches results
    
    Args:
        twitter_handle: Twitter handle to analyze (default: "Mason_Storika")
        max_wait_minutes: Maximum time to wait for job completion (default: 30 minutes)
    
    Returns:
        JSON string with engagement metrics and tweet data
    """
    # Create cache directory
    cache_dir = Path(__file__).parent.parent / "tweet_engagement_cache"
    cache_dir.mkdir(exist_ok=True)

    # Check for most recent cache file for this handle
    cache_pattern = f"engagement_{twitter_handle}_*.json"
    cache_files = sorted(cache_dir.glob(cache_pattern), reverse=True)

    if cache_files:
        most_recent = cache_files[0]
        # Extract timestamp from filename: engagement_{handle}_{timestamp}.json
        try:
            # Use regex to find timestamp pattern at end of filename
            # Format: 2025-10-12T16-39-32-489734 (colons and dots replaced with dashes)
            match = re.search(r'(\d{4}-\d{2}-\d{2}T[\d-]+)$', most_recent.stem)
            if not match:
                raise ValueError(f"Could not extract timestamp from filename: {most_recent.name}")

            file_timestamp_str = match.group(1)

            # Convert back to ISO format: replace dashes with colons in time part
            # Split by 'T' to separate date and time
            if 'T' in file_timestamp_str:
                date_part, time_part = file_timestamp_str.split('T')
                # Time part format: HH-MM-SS-microseconds -> HH:MM:SS.microseconds
                time_components = time_part.split('-')
                if len(time_components) >= 3:
                    # Reconstruct: HH:MM:SS.microseconds
                    reconstructed_time = f"{time_components[0]}:{time_components[1]}:{time_components[2]}"
                    if len(time_components) > 3:
                        reconstructed_time += f".{time_components[3]}"
                    file_timestamp_str = f"{date_part}T{reconstructed_time}"

            file_timestamp = datetime.fromisoformat(file_timestamp_str)
            time_diff = datetime.utcnow() - file_timestamp

            # If less than 1 hour old, use cached data
            if time_diff.total_seconds() < 3600:
                print(f"[CMO_AGENT] Using cached engagement data for @{twitter_handle} (age: {time_diff.total_seconds()/60:.1f} minutes)")
                with open(most_recent, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                cached_data["cached"] = True
                cached_data["cache_age_minutes"] = round(time_diff.total_seconds() / 60, 1)
                return json.dumps(cached_data, indent=2)
            else:
                print(f"[CMO_AGENT] Cache expired for @{twitter_handle} (age: {time_diff.total_seconds()/3600:.1f} hours)")
        except (ValueError, IndexError) as e:
            print(f"[CMO_AGENT] Error parsing cache timestamp: {e}")

    print(f"[CMO_AGENT] No recent cache found, fetching fresh engagement data for @{twitter_handle}")

    # Get Apify token
    token = os.getenv("APIFY_TOKEN")
    if not token:
        return json.dumps({
            "status": "failed",
            "error": "APIFY_TOKEN environment variable is not set",
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)

    # Initialize Apify client
    client = ApifyClient(token)
    actor_id = "apidojo/tweet-scraper"

    # Prepare input
    run_input = {
        "tweetLanguage": "en",
        "twitterHandles": [twitter_handle],
    }

    print(f"[CMO_AGENT] Launching Apify Tweet Scraper for @{twitter_handle}")

    try:
        # Start the Apify run
        run = client.actor(actor_id).start(run_input=run_input)
        run_id = run["id"]

        print(f"[CMO_AGENT] Tweet Scraper job started: {run_id}")
        print(f"[CMO_AGENT] View at: https://console.apify.com/actors/runs/{run_id}")

        # Poll for completion
        max_iterations = max_wait_minutes * 6  # Check every 10 seconds
        poll_interval = 10  # 10 seconds

        for iteration in range(max_iterations):
            # Get run status
            run_info = client.run(run_id).get()
            status = run_info.get("status")

            print(f"[CMO_AGENT] Job status: {status} (check {iteration + 1}/{max_iterations})")

            if status == "SUCCEEDED":
                print(f"[CMO_AGENT] Job completed successfully!")

                # Get dataset items
                dataset_id = run_info.get("defaultDatasetId")
                if not dataset_id:
                    return json.dumps({
                        "status": "failed",
                        "error": "No dataset found for completed run",
                        "run_id": run_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }, indent=2)

                # Fetch all items from dataset
                items = list(client.dataset(dataset_id).iterate_items())

                # Calculate engagement metrics using correct field names
                # Apify returns: likeCount, retweetCount, replyCount, viewCount
                total_tweets = len(items)
                total_likes = sum(item.get("likeCount", 0) for item in items)
                total_retweets = sum(item.get("retweetCount", 0) for item in items)
                total_replies = sum(item.get("replyCount", 0) for item in items)
                total_views = sum(item.get("viewCount", 0) for item in items)

                avg_likes = total_likes / total_tweets if total_tweets > 0 else 0
                avg_retweets = total_retweets / total_tweets if total_tweets > 0 else 0
                avg_replies = total_replies / total_tweets if total_tweets > 0 else 0
                avg_views = total_views / total_tweets if total_tweets > 0 else 0

                # Sort tweets by engagement (likes + retweets + replies)
                for item in items:
                    item["total_engagement"] = (
                        item.get("likeCount", 0) +
                        item.get("retweetCount", 0) +
                        item.get("replyCount", 0)
                    )

                top_tweets = sorted(
                    items,
                    key=lambda x: x.get("total_engagement", 0),
                    reverse=True
                )[:10]

                result = {
                    "status": "success",
                    "twitter_handle": twitter_handle,
                    "run_id": run_id,
                    "metrics": {
                        "total_tweets": total_tweets,
                        "total_likes": total_likes,
                        "total_retweets": total_retweets,
                        "total_replies": total_replies,
                        "total_views": total_views,
                        "avg_likes": round(avg_likes, 2),
                        "avg_retweets": round(avg_retweets, 2),
                        "avg_replies": round(avg_replies, 2),
                        "avg_views": round(avg_views, 2)
                    },
                    "top_tweets": [
                        {
                            "text": tweet.get("text", ""),
                            "url": tweet.get("url", ""),
                            "created_at": tweet.get("createdAt", ""),
                            "likes": tweet.get("likeCount", 0),
                            "retweets": tweet.get("retweetCount", 0),
                            "replies": tweet.get("replyCount", 0),
                            "views": tweet.get("viewCount", 0),
                            "total_engagement": tweet.get("total_engagement", 0)
                        }
                        for tweet in top_tweets
                    ],
                    "all_tweets": items,
                    "timestamp": datetime.utcnow().isoformat()
                }

                print(f"[CMO_AGENT] Engagement Analysis Complete:")
                print(f"  Total Tweets: {total_tweets}")
                print(f"  Avg Likes: {avg_likes:.2f}")
                print(f"  Avg Retweets: {avg_retweets:.2f}")
                print(f"  Avg Replies: {avg_replies:.2f}")

                # Save to cache
                timestamp_str = datetime.utcnow().isoformat().replace(':', '-').replace('.', '-')
                cache_filename = f"engagement_{twitter_handle}_{timestamp_str}.json"
                cache_filepath = cache_dir / cache_filename

                result["cached"] = False
                result["cache_age_minutes"] = 0

                try:
                    with open(cache_filepath, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2)
                    print(f"[CMO_AGENT] Saved engagement data to cache: {cache_filename}")
                except Exception as e:
                    print(f"[CMO_AGENT] Warning: Failed to save cache: {e}")

                return json.dumps(result, indent=2)

            elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                return json.dumps({
                    "status": "failed",
                    "error": f"Apify job {status}",
                    "run_id": run_id,
                    "run_status": status,
                    "timestamp": datetime.utcnow().isoformat()
                }, indent=2)

            # Wait before next check (unless this is the last iteration)
            if iteration < max_iterations - 1:
                time.sleep(poll_interval)

        # Timeout reached
        return json.dumps({
            "status": "timeout",
            "error": f"Job did not complete within {max_wait_minutes} minutes",
            "run_id": run_id,
            "run_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)

    except Exception as e:
        print(f"[CMO_AGENT ERROR] Failed to measure tweet engagement: {e}")
        import traceback
        traceback.print_exc()

        return json.dumps({
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)
