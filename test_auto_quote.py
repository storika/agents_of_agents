"""
Test script for auto_trending_repost
Automatically picks a random trending post and generates a comment
"""

from quote_agent import auto_trending_repost

def main():
    """Run auto trending repost"""

    print("="*70)
    print("Testing Auto Trending Repost")
    print("="*70)
    print("\nThis will:")
    print("1. Load trending posts from trend_data/")
    print("2. Randomly select one post")
    print("3. Generate a relevant comment using LLM")
    print("4. Show the result (dry run mode)\n")

    # Run auto trending repost
    result = auto_trending_repost(max_results=20)

    if result["status"] == "ready":
        print("\n✅ Success! Here's what we got:\n")
        print(f"Selected Post URL: {result['selected_post']['url']}")
        print(f"Post Text: {result['selected_post']['text'][:150]}...")
        print(f"\nGenerated Comment: {result['generated_comment']['text']}")
        print(f"Character Count: {result['generated_comment']['length']}/280")
        print(f"\n{result['preview']}")
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
