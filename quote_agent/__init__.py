"""
Quote Agent Package
Complete X API integration for automated quote tweeting with A2A protocol support
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

# Import agent and A2A interface
from quote_agent.agent import root_agent, execute, create_quote_tweet, post_quote_tweet

__all__ = [
    'search_recent_posts',
    'generate_quote_tweet_comment',
    'quote_tweet_post',
    'auto_repost_workflow',
    'print_workflow_result',
    'auto_trending_repost',
    'root_agent',
    'execute',
    'create_quote_tweet',
    'post_quote_tweet'
]

__version__ = '2.1.0'  # Updated with A2A protocol support
