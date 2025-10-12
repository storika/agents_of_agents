"""
Test script for the tweet engagement measurement tool
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import cmo_agent
sys.path.insert(0, os.path.dirname(__file__))

from cmo_agent.tools import measure_tweet_engagement


def test_tweet_engagement():
    """Test the tweet engagement measurement tool"""

    # Test with a real Twitter handle
    twitter_handle = "Mason_Storika"

    print(f"🔍 Testing tweet engagement measurement for @{twitter_handle}")
    print("=" * 60)

    # Note: This will actually launch an Apify job and wait for results
    # Make sure you have APIFY_TOKEN in your .env file
    result = measure_tweet_engagement(
        twitter_handle=twitter_handle,
        max_wait_minutes=5  # Short timeout for testing
    )

    print("\n📊 Results:")
    print("=" * 60)
    print(result)

    return result


if __name__ == "__main__":
    # Check if APIFY_TOKEN is set
    if not os.getenv("APIFY_TOKEN"):
        print("❌ Error: APIFY_TOKEN environment variable is not set")
        print("Please set it in your .env file")
        sys.exit(1)

    print("✅ APIFY_TOKEN found")
    print("\n⚠️  WARNING: This test will use Apify credits!")
    print("It will launch a real Apify job and poll for completion.")
    print("\nPress Ctrl+C to cancel, or wait 5 seconds to continue...")

    try:
        import time
        time.sleep(5)
        test_tweet_engagement()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
        sys.exit(0)
