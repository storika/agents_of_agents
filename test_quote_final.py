"""
Final test of quote tweet functionality
"""

from quote_agent.tools import load_trending_posts_from_data, generate_quote_tweet_comment, quote_to_x

print("=" * 70)
print("Final Quote Tweet Test")
print("=" * 70)

print("\n[Step 1] Loading trending posts...")
posts = load_trending_posts_from_data(max_results=3)

if not posts:
    print("❌ No posts loaded")
    exit(1)

print(f"✅ Loaded {len(posts)} posts")

# Use first post
post = posts[0]
tweet_url = post['url']
tweet_text = post['text']

print(f"\n[Step 2] Selected tweet to quote:")
print(f"   URL: {tweet_url}")
print(f"   Text: {tweet_text[:80]}...")

print(f"\n[Step 3] Generating comment...")
comment = generate_quote_tweet_comment(tweet_text)
print(f"✅ Generated comment:")
print(f"   {comment}")

print(f"\n[Step 4] Posting quote tweet...")
result = quote_to_x(
    tweet_url=tweet_url,
    comment=comment,
    actually_post=True,
    require_approval=False
)

import json
result_data = json.loads(result)

print(f"\n[Step 5] Result:")
print(f"   Status: {result_data.get('status')}")

if result_data.get('status') == 'published':
    print(f"✅ Quote tweet posted successfully!")
    print(f"   Quote ID: {result_data.get('quote_id')}")
    print(f"   URL: {result_data.get('url')}")
elif result_data.get('status') == 'failed':
    print(f"❌ Failed to post:")
    print(f"   Error: {result_data.get('error')}")
    print(f"   Message: {result_data.get('message')}")
else:
    print(f"⚠️ Unexpected status: {result_data.get('status')}")

print("\n" + "=" * 70)
