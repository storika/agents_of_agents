"""
Full test of quote agent with actual posting
"""

import json
from quote_agent.tools import auto_trending_repost, quote_to_x

print("=" * 70)
print("Testing Quote Agent - Full Flow with Actual Posting")
print("=" * 70)

# Test 1: auto_trending_repost to get tweet and comment
print("\n[Step 1] Finding trending tweet and generating comment...")
print("-" * 70)

result = auto_trending_repost(max_results=3)
result_data = result  # auto_trending_repost returns a dict, not a JSON string

print(f"Status: {result_data.get('status')}")

if result_data.get('status') == 'success':
    tweet_url = result_data.get('tweet_url')
    comment = result_data.get('comment')

    print(f"\n✅ Found tweet to quote:")
    print(f"   URL: {tweet_url}")
    print(f"   Comment: {comment}")

    # Test 2: Now actually post it
    print("\n[Step 2] Actually posting the quote tweet...")
    print("-" * 70)

    posting_result = quote_to_x(
        tweet_url=tweet_url,
        comment=comment,
        actually_post=True,  # Set to True to actually post
        require_approval=False
    )

    posting_data = json.loads(posting_result)
    print(f"\nPosting status: {posting_data.get('status')}")

    if posting_data.get('status') == 'success':
        print(f"✅ Quote tweet posted successfully!")
        print(f"   Quote tweet URL: {posting_data.get('quote_tweet_url')}")
    else:
        print(f"❌ Failed to post: {posting_data.get('error')}")
else:
    print(f"❌ Failed to find tweet: {result_data.get('error')}")

print("\n" + "=" * 70)
print("Test complete!")
print("=" * 70)
