"""
Quick test to check if quote_agent can load valid tweet URLs
"""

import json
from quote_agent.tools import load_trending_posts_from_data

print("=" * 70)
print("Testing Quote Agent - Trending Posts Loading")
print("=" * 70)

posts = load_trending_posts_from_data(max_results=10)

print(f"\n✅ Found {len(posts)} valid posts with tweet URLs")
print("\nFirst 3 posts:")
for i, post in enumerate(posts[:3], 1):
    print(f"\n{i}. Post ID: {post['id']}")
    print(f"   URL: {post['url']}")
    print(f"   Text preview: {post['text'][:80]}...")
    print(f"   Source: {post['source']}")
    print(f"   Has /status/ in URL: {'/status/' in post['url']}")

print("\n" + "=" * 70)
if posts:
    print("✅ Quote agent should now be able to post quote tweets!")
else:
    print("⚠️ No valid tweet URLs found in trend data")
print("=" * 70)
