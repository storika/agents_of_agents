"""
HR Validation Agent Tools
"""

import json
import os
import re
import time
from typing import List, Dict, Any, Optional
import weave
from apify_client import ApifyClient
from datetime import datetime

from weave.trace_server.trace_server_interface import CallsFilter


def get_recent_calls_as_json(
    limit: int = 100,
    filter: Optional[dict] = None,
    include_costs: bool = True,
    include_feedback: bool = True
) -> str:
    """
    Weave에서 최근 calls를 가져와서 JSON 형식으로 반환
    
    Args:
        limit: 가져올 call 개수
        filter: 필터 조건
        include_costs: 비용 정보 포함 여부
        include_feedback: 피드백 정보 포함 여부
    
    Returns:
        JSON string
    """
    # Use existing Weave client (initialized in agent.py via OTEL)
    import os
    client = weave.init(os.getenv("WANDB_PROJECT_ID", "mason-choi-storika/WeaveHacks2"))
    
    # Get calls - let Weave determine optimal columns
    # Note: columns parameter can cause 500 errors if we try to access fields not in the list
    calls_iter = client.get_calls(
        limit=limit,
        filter=filter,
        include_costs=include_costs,
        include_feedback=include_feedback,
        # Removed columns parameter to avoid 500 errors when accessing other fields
        sort_by=[{"field": "started_at", "direction": "desc"}]
    )
    
    calls = list(calls_iter)
    print(f"[HR_TOOLS] Found {len(calls)} calls")
    
    # Convert to JSON-serializable format
    calls_data = []
    for call in calls:
        call_dict = {
            "id": call.id,
            "trace_id": call.trace_id,
            "op_name": call.op_name,
            "started_at": call.started_at.isoformat() if call.started_at else None,
            "ended_at": call.ended_at.isoformat() if call.ended_at else None,
            "inputs": call.inputs if hasattr(call, 'inputs') else None,
            "output": call.output if hasattr(call, 'output') else None,
            "exception": call.exception if hasattr(call, 'exception') else None,
            "summary": call.summary if hasattr(call, 'summary') else None,
        }
        calls_data.append(call_dict)
    
    return json.dumps(calls_data, indent=2, default=str)


def get_calls_for_hr_validation(
    limit: int = 10,
    op_name_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    HR Validation Agent용 input 형식으로 calls 데이터 변환
    
    Args:
        limit: 가져올 call 개수
        op_name_filter: 특정 operation만 필터링 (예: "CMOAgent.run")
    
    Returns:
        HR agent input 형식의 dict
    """
    # Use existing Weave client (initialized in agent.py via OTEL)
    import os
    client = weave.init(os.getenv("WANDB_PROJECT_ID", "mason-choi-storika/WeaveHacks2"))
    
    # Build filter
    filter_dict = None
    if op_name_filter:
        filter_dict = {"op_names": [op_name_filter]}
    
    # Get calls - let Weave determine optimal columns
    # Note: columns parameter can cause 500 errors if we try to access fields not in the list
    calls_iter = client.get_calls(
        limit=limit,
        filter=CallsFilter(op_names=[op_name_filter]) if op_name_filter else None,
        include_costs=True,
        include_feedback=True,
        # Removed columns parameter to avoid 500 errors when accessing other fields
        sort_by=[{"field": "started_at", "direction": "desc"}]
    )
    
    calls = list(calls_iter)
    print(f"[HR_TOOLS] Found {len(calls)} calls for HR validation")
    
    if calls:
        print(f"[HR_TOOLS] Sample call (entire object):")
        print(f"[HR_TOOLS] {calls[0]}")
        print(f"[HR_TOOLS] Type: {type(calls[0])}")
        print(f"[HR_TOOLS] Dir: {dir(calls[0])}")
    
    # Convert to HR agent format
    agents_performance = []
    
    for call in calls:
        # Extract performance metrics from call
        agent_data = {
            "agent_name": call.op_name,
            "call_id": call.id,
            "execution_time_ms": None,
            "success": call.exception is None,
            "metrics": {}
        }
        
        # Calculate execution time
        if call.started_at and call.ended_at:
            duration = (call.ended_at - call.started_at).total_seconds() * 1000
            agent_data["execution_time_ms"] = duration
        
        # Extract metrics from summary
        if hasattr(call, 'summary') and call.summary:
            summary = call.summary
            if isinstance(summary, dict):
                # Extract Weave metrics
                if 'weave' in summary:
                    weave_data = summary['weave']
                    if 'costs' in weave_data:
                        agent_data["metrics"]["costs"] = weave_data['costs']
                    if 'feedback' in weave_data:
                        agent_data["metrics"]["feedback"] = weave_data['feedback']
        
        agents_performance.append(agent_data)
    
    return {
        "iteration": 0,  # 필요시 파라미터로 받기
        "agents_performance": agents_performance,
        "total_calls": len(calls),
        "timestamp": calls[0].started_at.isoformat() if calls and calls[0].started_at else None
    }


# Test code (comment out in production)
if __name__ == "__main__":
    # Test 1: Get as JSON
    print("=" * 70)
    print("Test 1: Get calls as JSON")
    print("=" * 70)
    json_data = get_recent_calls_as_json(limit=5)
    print(json_data[:500] + "...")
    
    print("\n" + "=" * 70)
    print("Test 2: Get for HR validation")
    print("=" * 70)
    hr_input = get_calls_for_hr_validation(limit=10)
    print(json.dumps(hr_input, indent=2, default=str)[:800] + "...")


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
    from pathlib import Path

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
                print(f"[HR_AGENT] Using cached engagement data for @{twitter_handle} (age: {time_diff.total_seconds()/60:.1f} minutes)")
                with open(most_recent, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                cached_data["cached"] = True
                cached_data["cache_age_minutes"] = round(time_diff.total_seconds() / 60, 1)
                return json.dumps(cached_data, indent=2)
            else:
                print(f"[HR_AGENT] Cache expired for @{twitter_handle} (age: {time_diff.total_seconds()/3600:.1f} hours)")
        except (ValueError, IndexError) as e:
            print(f"[HR_AGENT] Error parsing cache timestamp: {e}")

    print(f"[HR_AGENT] No recent cache found, fetching fresh engagement data for @{twitter_handle}")

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

    print(f"[HR_AGENT] Launching Apify Tweet Scraper for @{twitter_handle}")

    try:
        # Start the Apify run
        run = client.actor(actor_id).start(run_input=run_input)
        run_id = run["id"]

        print(f"[HR_AGENT] Tweet Scraper job started: {run_id}")
        print(f"[HR_AGENT] View at: https://console.apify.com/actors/runs/{run_id}")

        # Poll for completion
        max_iterations = max_wait_minutes * 6  # Check every 10 seconds
        poll_interval = 10  # 10 seconds

        for iteration in range(max_iterations):
            # Get run status
            run_info = client.run(run_id).get()
            status = run_info.get("status")

            print(f"[HR_AGENT] Job status: {status} (check {iteration + 1}/{max_iterations})")

            if status == "SUCCEEDED":
                print(f"[HR_AGENT] Job completed successfully!")

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

                print(f"[HR_AGENT] Engagement Analysis Complete:")
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
                    print(f"[HR_AGENT] Saved engagement data to cache: {cache_filename}")
                except Exception as e:
                    print(f"[HR_AGENT] Warning: Failed to save cache: {e}")

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
        print(f"[HR_AGENT ERROR] Failed to measure tweet engagement: {e}")
        import traceback
        traceback.print_exc()

        return json.dumps({
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, indent=2)