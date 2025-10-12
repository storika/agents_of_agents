"""
Test Twitter API authentication and permissions
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Testing Twitter API Authentication")
print("=" * 70)

# Check credentials
TW_CLIENT_ID = os.getenv("TW_CLIENT_ID")
TW_CLIENT_SECRET = os.getenv("TW_CLIENT_SECRET")
TW_ACCESS_TOKEN = os.getenv("TW_ACCESS_TOKEN")
TW_ACCESS_SECRET = os.getenv("TW_ACCESS_SECRET")

print("\n[Step 1] Checking credentials...")
if all([TW_CLIENT_ID, TW_CLIENT_SECRET, TW_ACCESS_TOKEN, TW_ACCESS_SECRET]):
    print("✅ All OAuth 1.0a credentials found")
    print(f"   TW_CLIENT_ID: {TW_CLIENT_ID[:10]}...")
    print(f"   TW_CLIENT_SECRET: {TW_CLIENT_SECRET[:10]}...")
    print(f"   TW_ACCESS_TOKEN: {TW_ACCESS_TOKEN[:10]}...")
    print(f"   TW_ACCESS_SECRET: {TW_ACCESS_SECRET[:10]}...")
else:
    print("❌ Missing credentials")
    exit(1)

print("\n[Step 2] Initializing pytwitter API...")
try:
    from pytwitter import Api

    api = Api(
        consumer_key=TW_CLIENT_ID,
        consumer_secret=TW_CLIENT_SECRET,
        access_token=TW_ACCESS_TOKEN,
        access_secret=TW_ACCESS_SECRET,
    )
    print("✅ API initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize API: {e}")
    exit(1)

print("\n[Step 3] Testing API access - Getting authenticated user info...")
try:
    # Get authenticated user's info
    me = api.get_me()
    if me and me.data:
        print(f"✅ Authenticated as: @{me.data.username} (ID: {me.data.id})")
        print(f"   Name: {me.data.name}")
    else:
        print("❌ Could not get user info")
except Exception as e:
    print(f"❌ Failed to get user info: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"   This suggests the tokens may not have the correct permissions")

print("\n[Step 4] Testing write permissions - Creating a test tweet...")
try:
    # Try to create a simple tweet
    test_text = "Test tweet from pytwitter - OAuth 1.0a authentication test"
    response = api.create_tweet(text=test_text)

    if response and response.data:
        print(f"✅ Successfully created tweet!")
        print(f"   Tweet ID: {response.data.id}")
        print(f"   Text: {response.data.text}")

        # Try to delete it immediately
        print("\n[Step 5] Cleaning up - Deleting test tweet...")
        delete_response = api.delete_tweet(tweet_id=response.data.id)
        if delete_response:
            print("✅ Test tweet deleted successfully")
    else:
        print("❌ Failed to create tweet - no response data")

except Exception as e:
    print(f"❌ Failed to create tweet: {e}")
    print(f"   Error details: {type(e).__name__}")
    if hasattr(e, 'response'):
        print(f"   Response status: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}")
        print(f"   Response body: {e.response.text if hasattr(e.response, 'text') else 'N/A'}")

    print("\n   This 401 error typically means:")
    print("   1. The access tokens are invalid or expired")
    print("   2. The app doesn't have write permissions enabled")
    print("   3. The tokens were generated with read-only scope")
    print("\n   To fix:")
    print("   1. Go to https://developer.twitter.com/en/portal/dashboard")
    print("   2. Select your app")
    print("   3. Go to 'User authentication settings'")
    print("   4. Ensure 'Read and write' permissions are enabled")
    print("   5. Regenerate your access tokens AFTER changing permissions")

print("\n" + "=" * 70)
print("Authentication test complete")
print("=" * 70)
