"""
Repost Agent Simple Run Example
Demonstrates creating engaging quote tweets
"""

import json
from quote_agent.agent import create_quote_tweet, post_quote_tweet


def example_1_quote_specific_tweet():
    """Example 1: Create a quote tweet for a specific tweet text"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Quote Tweet with Specific Text")
    print("="*70)

    tweet_text = "Just shipped multi-agent systems in production. The debugging complexity is real but the velocity gains are worth it. 🚀"
    author = "@BuilderAI"

    result = create_quote_tweet(
        tweet_text=tweet_text,
        author=author,
        strategy="experience"  # Share your experience
    )

    if result.get("status") == "ready_to_post":
        print(f"\n✅ Quote tweet ready!")
        print(f"\nOriginal Tweet by {result['original_tweet']['author']}:")
        print(f"  {result['original_tweet']['text']}")
        print(f"\nYour Comment ({result['selected_comment']['strategy']} strategy):")
        print(f"  {result['selected_comment']['comment']}")
        print(f"\nScore: {result['selected_comment']['overall_score']:.2f}")
        print(f"Character Count: {result['selected_comment']['character_count']}/280")

        # Show all generated options
        print(f"\n📋 Other Options Generated ({len(result['comment_options'])} total):")
        for i, option in enumerate(result['comment_options'][:3], 1):
            print(f"  {i}. [{option['strategy']}] {option['comment'][:60]}...")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")


def example_2_find_and_quote():
    """Example 2: Find trending tweets and create quote tweet"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Find Trending Tweet & Quote It")
    print("="*70)

    result = create_quote_tweet(
        topic="AI agents",
        strategy="auto"  # Let agent choose best strategy
    )

    if result.get("status") == "ready_to_post":
        print(f"\n✅ Found trending tweet and created quote!")
        print(f"\nOriginal Tweet by {result['original_tweet']['author']}:")
        print(f"  {result['original_tweet']['text'][:120]}...")
        print(f"\nAuto-Selected Strategy: {result['selected_comment']['strategy']}")
        print(f"\nYour Comment:")
        print(f"  {result['selected_comment']['comment']}")
        print(f"\nScore: {result['selected_comment']['overall_score']:.2f}")

        # Show engagement tips
        print(f"\n💡 Engagement Tips:")
        for tip in result['engagement_tips']:
            print(f"  - {tip}")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")


def example_3_compare_strategies():
    """Example 3: Compare different strategies for the same tweet"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Compare Different Strategies")
    print("="*70)

    tweet_text = "Debugging production AI agents at 2am is a unique kind of pain. Non-deterministic failures are the worst."
    author = "@DevOps"

    strategies = ["experience", "question", "analysis", "reaction"]

    print(f"\nOriginal Tweet: {tweet_text}\n")

    for strategy in strategies:
        result = create_quote_tweet(
            tweet_text=tweet_text,
            author=author,
            strategy=strategy
        )

        if result.get("status") == "ready_to_post":
            comment = result['selected_comment']
            print(f"[{strategy.upper()}] (score: {comment['overall_score']:.2f})")
            print(f"  {comment['comment']}")
            print()


def example_4_post_dry_run():
    """Example 4: Create and post (dry run)"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Create & Post Quote Tweet (Dry Run)")
    print("="*70)

    # First create the quote tweet
    result = create_quote_tweet(
        tweet_text="The future of AI is orchestrated teams of specialized agents working together.",
        author="@AIResearcher",
        strategy="analysis"
    )

    if result.get("status") == "ready_to_post":
        tweet_url = result['original_tweet']['url']
        comment = result['selected_comment']['comment']

        print(f"\n📝 Created quote tweet:")
        print(f"  Comment: {comment}")
        print(f"  Score: {result['selected_comment']['overall_score']:.2f}")

        # Post it (dry run)
        print(f"\n📤 Posting (dry run mode)...")
        post_result = post_quote_tweet(
            tweet_url=tweet_url,
            comment=comment,
            dry_run=True  # Safe - won't actually post
        )

        if post_result.get("status") == "dry_run_success":
            print(f"✅ Dry run successful!")
            print(f"  Would post: {post_result['quote_tweet']['comment'][:60]}...")
            print(f"  Character count: {post_result['quote_tweet']['character_count']}")
            print(f"\n💡 Set dry_run=False to actually post to Twitter")
        else:
            print(f"❌ Error: {post_result.get('message', 'Unknown')}")


def example_5_json_output():
    """Example 5: Get full JSON output for integration"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Full JSON Output for Integration")
    print("="*70)

    result = create_quote_tweet(
        tweet_text="Building in public is hard but worth it. Shipped 5 features this week!",
        author="@IndieHacker",
        strategy="reaction"
    )

    # Pretty print the full result
    print(f"\n📄 Full JSON Result:")
    print(json.dumps(result, indent=2))


def main():
    """Run all examples"""
    print("\n" + "🚀" * 35)
    print("REPOST AGENT - USAGE EXAMPLES")
    print("🚀" * 35)

    try:
        example_1_quote_specific_tweet()
        example_2_find_and_quote()
        example_3_compare_strategies()
        example_4_post_dry_run()
        example_5_json_output()

        print("\n" + "="*70)
        print("✨ ALL EXAMPLES COMPLETED")
        print("="*70)
        print("\n🎯 Key Takeaways:")
        print("  1. Use create_quote_tweet() to generate quote tweets")
        print("  2. Choose strategy: auto, experience, question, analysis, reaction, context, connect")
        print("  3. Get scored options - select the best one")
        print("  4. Use post_quote_tweet() with dry_run=True to test")
        print("  5. All actions are tracked in Weave for observability")
        print("\n📚 See README.md for more details")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
