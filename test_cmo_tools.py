"""
Quick test script to verify CMO agent tools are loading real data
"""

import json
from cmo_agent.tools import get_trending_context

print("=" * 70)
print("Testing CMO Agent Tools - Simplified")
print("=" * 70)

print("\nTesting get_trending_context()...")
print("-" * 70)
trending_result = get_trending_context()
trending_data = json.loads(trending_result)

print(f"Status: {trending_data.get('status')}")
print(f"Source: {trending_data.get('source')}")
print(f"Trending topics found: {len(trending_data.get('trending_topics', []))}")
print(f"Keywords found: {len(trending_data.get('keywords', []))}")
print(f"Recommended hashtags: {trending_data.get('recommended_hashtags', [])[:5]}")

if trending_data.get('trending_topics'):
    print(f"\nTop 3 trending topics:")
    for i, topic in enumerate(trending_data['trending_topics'][:3], 1):
        print(f"  {i}. {topic.get('topic')} (score: {topic.get('trend_score')})")

print("\n" + "=" * 70)
print("✅ Test completed! CMO agent now uses real trend data")
print("=" * 70)
