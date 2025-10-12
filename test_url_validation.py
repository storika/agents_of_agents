"""
Test URL validation for quote_agent and reply_agent
"""

import json
from quote_agent.tools import quote_to_x
from reply_agent.tools import post_reply

print("=" * 70)
print("Testing URL Validation for Quote and Reply Agents")
print("=" * 70)

# Test cases
test_urls = [
    {
        "url": "https://twitter.com/search?q=%23PatriotsWin&src=hashtag_click",
        "description": "Search URL (should be rejected)",
        "should_pass": False
    },
    {
        "url": "https://x.com/trendforprem/status/1977189495910129768",
        "description": "Valid tweet URL",
        "should_pass": True
    },
    {
        "url": "https://twitter.com/username",
        "description": "Profile URL (should be rejected)",
        "should_pass": False
    },
    {
        "url": "https://twitter.com/ATLHawks/status/1977173586499498467",
        "description": "Valid tweet URL from twitter.com",
        "should_pass": True
    }
]

print("\n[TEST 1: Quote Agent URL Validation]")
print("-" * 70)

for i, test_case in enumerate(test_urls, 1):
    url = test_case["url"]
    description = test_case["description"]
    should_pass = test_case["should_pass"]

    print(f"\nTest {i}: {description}")
    print(f"URL: {url}")

    result = quote_to_x(
        tweet_url=url,
        comment="Test comment",
        actually_post=False
    )

    result_data = json.loads(result)
    status = result_data.get("status")

    if should_pass:
        if status in ["queued", "success", "simulated"]:  # simulated is valid when actually_post=False
            print(f"✅ PASS - URL accepted (status: {status})")
        else:
            print(f"❌ FAIL - URL rejected but should pass (status: {status})")
    else:
        if status == "failed":
            print(f"✅ PASS - URL rejected correctly (error: {result_data.get('error')})")
        else:
            print(f"❌ FAIL - URL accepted but should be rejected (status: {status})")

print("\n" + "=" * 70)
print("[TEST 2: Reply Agent URL Validation]")
print("-" * 70)

for i, test_case in enumerate(test_urls, 1):
    url = test_case["url"]
    description = test_case["description"]
    should_pass = test_case["should_pass"]

    print(f"\nTest {i}: {description}")
    print(f"URL: {url}")

    result = post_reply(
        tweet_url=url,
        reply_text="Test reply",
        dry_run=True
    )

    result_data = json.loads(result)
    status = result_data.get("status")

    if should_pass:
        if status in ["simulated", "posted"]:
            print(f"✅ PASS - URL accepted (status: {status})")
        else:
            print(f"❌ FAIL - URL rejected but should pass (status: {status})")
    else:
        if status == "error":
            print(f"✅ PASS - URL rejected correctly (error: {result_data.get('error')})")
        else:
            print(f"❌ FAIL - URL accepted but should be rejected (status: {status})")

print("\n" + "=" * 70)
print("URL Validation Tests Complete!")
print("=" * 70)
