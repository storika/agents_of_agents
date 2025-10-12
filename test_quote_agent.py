"""
Test script for Repost Agent
Demonstrates quote tweet generation with different strategies
"""

import json
from quote_agent.agent import create_quote_tweet, root_agent
from quote_agent.tools import (
    find_trending_tweets_tool,
    generate_repost_comment_tool,
    analyze_tweet_for_repost,
    extract_tweet_id
)


def test_find_trending_tweets():
    """Test finding trending tweets on a topic"""
    print("\n" + "="*60)
    print("TEST 1: Find Trending Tweets")
    print("="*60)

    result = find_trending_tweets_tool(topic="AI agents", max_results=3)
    data = json.loads(result)

    print(f"✅ Found {data['total_found']} tweets about '{data['query']}'")
    print(f"\nTop tweet:")
    top_tweet = data['tweets'][0]
    print(f"  Author: {top_tweet['author']}")
    print(f"  Text: {top_tweet['text'][:100]}...")
    print(f"  Engagement: {top_tweet['metrics']['likes']} likes, {top_tweet['metrics']['retweets']} retweets")


def test_generate_comment():
    """Test generating repost comments with different strategies"""
    print("\n" + "="*60)
    print("TEST 2: Generate Repost Comments")
    print("="*60)

    tweet_text = "Just shipped a new multi-agent system in production. The debugging complexity is real but the velocity gains are worth it."

    strategies = ["auto", "experience", "question", "analysis"]

    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")
        result = generate_repost_comment_tool(
            tweet_text=tweet_text,
            author="@BuilderAI",
            strategy=strategy
        )
        data = json.loads(result)

        if data['generated_comments']:
            top = data['generated_comments'][0]
            print(f"Comment: {top['comment']}")
            print(f"Score: {top['scores']['overall']:.2f}")
            print(f"Characters: {top['character_count']}/280")


def test_analyze_tweet():
    """Test tweet analysis for strategy recommendation"""
    print("\n" + "="*60)
    print("TEST 3: Analyze Tweet for Best Strategy")
    print("="*60)

    test_tweets = [
        "Just shipped a new feature in 2 hours using Claude. The velocity is unreal.",
        "Unpopular opinion: Most teams don't need multi-agent systems. Start simple.",
        "Debugging AI agents at 2am is a special kind of pain. How do you handle non-deterministic failures?",
        "Here's what nobody tells you about AI agents: the infrastructure complexity is 10x what you expect."
    ]

    for tweet in test_tweets:
        result = analyze_tweet_for_repost(tweet)
        data = json.loads(result)
        print(f"\nTweet: {tweet[:60]}...")
        print(f"  Themes: {', '.join(data['detected_themes'])}")
        print(f"  Recommended: {data['recommended_strategy']}")
        print(f"  Reasoning: {data['reasoning']}")


def test_create_quote_tweet_full():
    """Test full quote tweet creation workflow"""
    print("\n" + "="*60)
    print("TEST 4: Full Quote Tweet Creation")
    print("="*60)

    # Test with direct tweet text
    tweet_text = "We've been running multi-agent systems in production for 3 months. Lessons learned: 1) Observability is critical 2) Start with fewer agents 3) Clear communication protocols are everything"

    result = create_quote_tweet(
        tweet_text=tweet_text,
        author="@ProductionAI",
        strategy="experience"
    )

    if "error" not in result:
        print(f"✅ Quote tweet created successfully")
        print(f"Status: {result.get('status', 'N/A')}")
        if "selected_comment" in result:
            print(f"\nSelected Comment:")
            print(f"  {result['selected_comment'].get('comment', 'N/A')}")
            print(f"  Strategy: {result['selected_comment'].get('strategy', 'N/A')}")
            print(f"  Score: {result['selected_comment'].get('overall_score', 'N/A'):.2f}")
            print(f"  Length: {result['selected_comment'].get('character_count', 'N/A')} chars")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")


def test_extract_tweet_id():
    """Test extracting tweet ID from URLs"""
    print("\n" + "="*60)
    print("TEST 5: Extract Tweet ID from URL")
    print("="*60)

    test_urls = [
        "https://twitter.com/example/status/1234567890",
        "https://x.com/example/status/9876543210?s=20",
        "https://twitter.com/user/status/1111111111111111111"
    ]

    for url in test_urls:
        tweet_id = extract_tweet_id(url)
        print(f"URL: {url}")
        print(f"  Extracted ID: {tweet_id}")


def test_quote_tweet_with_topic():
    """Test creating quote tweet by finding trending topic"""
    print("\n" + "="*60)
    print("TEST 6: Quote Tweet from Topic Search")
    print("="*60)

    result = create_quote_tweet(
        topic="AI agents",
        strategy="auto"  # Let it auto-select strategy
    )

    if "error" not in result:
        print(f"✅ Quote tweet created from topic search")
        print(f"\nOriginal Tweet:")
        print(f"  Author: {result['original_tweet']['author']}")
        print(f"  Text: {result['original_tweet']['text'][:80]}...")
        print(f"\nSelected Comment:")
        print(f"  {result['selected_comment']['comment']}")
        print(f"  Strategy: {result['selected_comment']['strategy']}")
        print(f"  Score: {result['selected_comment']['overall_score']:.2f}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 REPOST AGENT TEST SUITE")
    print("="*60)

    try:
        # Tool tests
        test_find_trending_tweets()
        test_generate_comment()
        test_analyze_tweet()
        test_extract_tweet_id()

        # Integration tests
        test_create_quote_tweet_full()
        test_quote_tweet_with_topic()

        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        print("\nRepost Agent is ready to use!")
        print("\nUsage examples:")
        print("  1. create_quote_tweet(tweet_text='...', author='@user', strategy='experience')")
        print("  2. create_quote_tweet(tweet_url='https://twitter.com/user/status/123')")
        print("  3. create_quote_tweet(topic='AI agents', strategy='auto')")
        print("  4. post_quote_tweet(tweet_url='...', comment='...', dry_run=True)")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
