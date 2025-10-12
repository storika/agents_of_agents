"""
Quote Agent Package
Complete X API integration for automated quote tweeting
"""

# Import X API tools
from quote_agent.tools import (
    search_recent_posts,
    generate_quote_tweet_comment,
    quote_tweet_post,
    auto_repost_workflow,
    print_workflow_result,
    auto_trending_repost
)

__all__ = [
    'search_recent_posts',
    'generate_quote_tweet_comment',
    'quote_tweet_post',
    'auto_repost_workflow',
    'print_workflow_result',
    'auto_trending_repost'
]

__version__ = '2.0.0'  # Updated with X API integration
