"""
Test quote tweet with OAuth 2.0
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("Testing Quote Tweet with OAuth 2.0")
print("=" * 70)

# Check OAuth 2.0 token
TW_OAUTH2_ACCESS_TOKEN = os.getenv("TW_OAUTH2_ACCESS_TOKEN")

if not TW_OAUTH2_ACCESS_TOKEN:
    print("❌ TW_OAUTH2_ACCESS_TOKEN not found")
    exit(1)

print("\n✅ OAuth 2.0 token found")
print(f"   Token: {TW_OAUTH2_ACCESS_TOKEN[:20]}...")

print("\n[Test 1] Initialize pytwitter with OAuth 2.0...")
try:
    from pytwitter import Api

    api = Api(bearer_token=TW_OAUTH2_ACCESS_TOKEN)
    print("✅ API initialized")
except Exception as e:
    print(f"❌ Failed: {e}")
    exit(1)

print("\n[Test 2] Create a simple test tweet...")
try:
    test_tweet = api.create_tweet(text="Test tweet for quote testing - will be deleted")
    if test_tweet and test_tweet.data:
        tweet_id = test_tweet.data.id
        print(f"✅ Created test tweet: {tweet_id}")
    else:
        print("❌ Failed to create test tweet")
        exit(1)
except Exception as e:
    print(f"❌ Failed to create tweet: {e}")
    exit(1)

print("\n[Test 3] Create a quote tweet...")
try:
    quote_text = "This is a quote tweet test - will be deleted"
    quote_tweet = api.create_tweet(text=quote_text, quote_tweet_id=str(tweet_id))

    if quote_tweet and quote_tweet.data:
        quote_id = quote_tweet.data.id
        print(f"✅ Created quote tweet: {quote_id}")
        print(f"   Quote text: {quote_tweet.data.text}")
    else:
        print("❌ Failed to create quote tweet - no response data")
        # Clean up original tweet
        api.delete_tweet(tweet_id=str(tweet_id))
        exit(1)
except Exception as e:
    print(f"❌ Failed to create quote tweet: {e}")
    print(f"   Error type: {type(e).__name__}")
    # Clean up original tweet
    try:
        api.delete_tweet(tweet_id=str(tweet_id))
    except:
        pass
    exit(1)

print("\n[Test 4] Cleanup - Delete both tweets...")
try:
    # Delete quote tweet first
    api.delete_tweet(tweet_id=str(quote_id))
    print(f"✅ Deleted quote tweet: {quote_id}")

    # Delete original tweet
    api.delete_tweet(tweet_id=str(tweet_id))
    print(f"✅ Deleted original tweet: {tweet_id}")
except Exception as e:
    print(f"⚠️ Cleanup warning: {e}")

print("\n" + "=" * 70)
print("✅ All tests passed! Quote tweets work with OAuth 2.0")
print("=" * 70)
