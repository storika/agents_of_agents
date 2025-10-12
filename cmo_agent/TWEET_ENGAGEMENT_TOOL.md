# Tweet Engagement Measurement Tool

## Overview

The `measure_tweet_engagement` tool measures engagement metrics for past tweets from a Twitter handle using Apify's Tweet Scraper actor (`apidojo/tweet-scraper`).

## Features

- **Smart Caching**: Automatically caches results for 1 hour to avoid unnecessary API calls
  - Checks for recent cached data before launching new jobs
  - Returns cached data if available (< 1 hour old)
  - Saves results to `tweet_engagement_cache/` directory
- **Automated Job Launch**: Launches Apify Tweet Scraper jobs programmatically
- **Fast Polling**: Checks job status every 10 seconds until completion
- **Comprehensive Metrics**: Returns detailed engagement data including:
  - Total tweets analyzed
  - Total and average likes, retweets, replies, views
  - Top 10 performing tweets
  - Full dataset of all tweets
- **Error Handling**: Gracefully handles timeouts, failures, and API errors

## Usage

### In CMO Agent

The tool is automatically available to the CMO agent. The agent can call it to analyze performance:

```python
# The CMO agent will call this internally
# If no handle specified, defaults to "Mason_Storika"
result = measure_tweet_engagement()

# Or specify a different handle
result = measure_tweet_engagement(
    twitter_handle="elonmusk",
    max_wait_minutes=30
)
```

### Standalone Usage

```python
from cmo_agent.tools import measure_tweet_engagement

# Measure engagement for default handle (Mason_Storika)
result_json = measure_tweet_engagement()

# Or measure for a specific handle
result_json = measure_tweet_engagement(
    twitter_handle="your_handle",
    max_wait_minutes=30  # Optional, default is 30 minutes
)

# Parse the JSON result
import json
result = json.loads(result_json)

# Access metrics
metrics = result["metrics"]
print(f"Average Likes: {metrics['avg_likes']}")
print(f"Average Retweets: {metrics['avg_retweets']}")

# View top performing tweets
for tweet in result["top_tweets"]:
    print(f"{tweet['text'][:50]}... - {tweet['total_engagement']} engagement")
```

## Response Format

### Success Response

```json
{
  "status": "success",
  "twitter_handle": "Mason_Storika",
  "run_id": "abc123xyz",
  "cached": false,
  "cache_age_minutes": 0,
  "metrics": {
    "total_tweets": 50,
    "total_likes": 1250,
    "total_retweets": 320,
    "total_replies": 180,
    "total_views": 45000,
    "avg_likes": 25.0,
    "avg_retweets": 6.4,
    "avg_replies": 3.6,
    "avg_views": 900.0
  },
  "top_tweets": [
    {
      "text": "Just launched our new AI agent...",
      "url": "https://twitter.com/...",
      "created_at": "2025-01-10T12:00:00Z",
      "likes": 150,
      "retweets": 45,
      "replies": 23,
      "views": 5000,
      "total_engagement": 218
    }
  ],
  "all_tweets": [...],
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Note**: When data is returned from cache:
- `cached` will be `true`
- `cache_age_minutes` will show how old the cached data is (e.g., `15.3` for 15.3 minutes old)

### Error Response

```json
{
  "status": "failed",
  "error": "Error message here",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Timeout Response

```json
{
  "status": "timeout",
  "error": "Job did not complete within 30 minutes",
  "run_id": "abc123xyz",
  "run_status": "RUNNING",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## How It Works

1. **Check Cache**: Looks for recent cached data in `tweet_engagement_cache/` directory
   - If found and < 1 hour old: Returns cached data immediately
   - If not found or expired: Proceeds to fetch fresh data
2. **Initialize Apify Client**: Uses `APIFY_TOKEN` from environment variables
3. **Launch Job**: Starts the `apidojo/tweet-scraper` actor with the specified Twitter handle
4. **Poll Status**: Checks job status every 10 seconds
5. **Retrieve Results**: Once job succeeds, fetches all tweets from the dataset
6. **Calculate Metrics**: Computes engagement statistics and identifies top performers
7. **Save to Cache**: Stores results in JSON file with timestamp
8. **Return JSON**: Returns comprehensive data in JSON format

## Configuration

### Environment Variables

- `APIFY_TOKEN`: Required. Your Apify API token

### Parameters

- `twitter_handle` (str, optional): Twitter handle to analyze (without @). Defaults to "Mason_Storika" if not provided
- `max_wait_minutes` (int, optional): Maximum time to wait for job completion (default: 30)

## Integration with CMO Agent

The tool is integrated into the CMO agent's toolkit and can be used to:

1. **Analyze Past Performance**: Understand what content types perform best
2. **Inform Strategy**: Use engagement data to guide content decisions
3. **Benchmark Progress**: Track improvement over time
4. **Identify Top Content**: Learn from highest-performing tweets

The CMO agent's instruction now includes guidance on when to use this tool:

```
ANALYTICS TOOLS:
1. **measure_tweet_engagement**: Analyze past tweets and engagement metrics
   - Use to: Understand what content performs best
   - Data: Likes, retweets, replies, views, top performing tweets
   - When to use: Before planning strategy, when user asks about performance
```

## Testing

Run the test script to verify the tool works:

```bash
python test_tweet_engagement.py
```

**Warning**: This will consume Apify credits as it launches a real job.

## Apify Actor Details

- **Actor ID**: `apidojo/tweet-scraper`
- **Input Format**:
  ```json
  {
    "tweetLanguage": "en",
    "twitterHandles": ["Mason_Storika"]
  }
  ```
- **Documentation**: https://console.apify.com/actors/apidojo~tweet-scraper

## Error Handling

The tool handles several error scenarios:

1. **Missing APIFY_TOKEN**: Returns error immediately
2. **Job Failure**: Detects FAILED, ABORTED, TIMED-OUT statuses
3. **Timeout**: Returns timeout error if max_wait_minutes exceeded
4. **API Errors**: Catches and returns exception details
5. **Empty Dataset**: Handles cases where no tweets are returned

## Future Enhancements

Potential improvements:

- Add date range filtering for tweets
- Support multiple Twitter handles in one call
- Cache results to avoid re-scraping
- Add sentiment analysis of engagement patterns
- Export data to CSV/Excel formats
- Integration with analytics dashboards
