"""
Test X API Credentials
Diagnose credential issues and test different authentication methods
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("X API CREDENTIAL TEST")
print("="*70)

# Check what credentials are available
print("\n📋 Available Credentials:")
print("-"*70)

TW_CLIENT_ID = os.getenv("TW_CLIENT_ID")
TW_CLIENT_SECRET = os.getenv("TW_CLIENT_SECRET")
TW_ACCESS_TOKEN = os.getenv("TW_ACCESS_TOKEN")
TW_ACCESS_SECRET = os.getenv("TW_ACCESS_SECRET")
TW_OAUTH2_ACCESS_TOKEN = os.getenv("TW_OAUTH2_ACCESS_TOKEN")
TW_OAUTH2_REFRESH_TOKEN = os.getenv("TW_OAUTH2_REFRESH_TOKEN")

print(f"TW_CLIENT_ID: {'✅ Set' if TW_CLIENT_ID else '❌ Not set'}")
print(f"TW_CLIENT_SECRET: {'✅ Set' if TW_CLIENT_SECRET else '❌ Not set'}")
print(f"TW_ACCESS_TOKEN: {'✅ Set' if TW_ACCESS_TOKEN else '❌ Not set'}")
print(f"TW_ACCESS_SECRET: {'✅ Set' if TW_ACCESS_SECRET else '❌ Not set'}")
print(f"TW_OAUTH2_ACCESS_TOKEN: {'✅ Set' if TW_OAUTH2_ACCESS_TOKEN else '❌ Not set'}")
print(f"TW_OAUTH2_REFRESH_TOKEN: {'✅ Set' if TW_OAUTH2_REFRESH_TOKEN else '❌ Not set'}")

# Try to initialize the API
print("\n🔧 Testing API Initialization:")
print("-"*70)

try:
    from pytwitter import Api

    # Test OAuth 1.0a
    if all([TW_CLIENT_ID, TW_CLIENT_SECRET, TW_ACCESS_TOKEN, TW_ACCESS_SECRET]):
        print("\n1️⃣ Testing OAuth 1.0a...")
        try:
            api = Api(
                consumer_key=TW_CLIENT_ID,
                consumer_secret=TW_CLIENT_SECRET,
                access_token=TW_ACCESS_TOKEN,
                access_secret=TW_ACCESS_SECRET
            )
            print("   ✅ API instance created")

            # Try to get authenticated user
            try:
                # This should work if credentials are valid
                user = api.get_me()
                if user and user.data:
                    print(f"   ✅ Authenticated as: @{user.data.username}")
                    print(f"   ✅ User ID: {user.data.id}")
                else:
                    print("   ⚠️ Could not fetch user info (might need additional permissions)")
            except Exception as e:
                print(f"   ❌ Authentication test failed: {e}")

        except Exception as e:
            print(f"   ❌ Failed to create API: {e}")
    else:
        print("\n1️⃣ OAuth 1.0a: ❌ Missing credentials")

    # Test OAuth 2.0
    if TW_OAUTH2_ACCESS_TOKEN:
        print("\n2️⃣ Testing OAuth 2.0...")
        try:
            api2 = Api(
                oauth_flow=True,
                access_token=TW_OAUTH2_ACCESS_TOKEN
            )
            print("   ✅ API instance created")

            try:
                user = api2.get_me()
                if user and user.data:
                    print(f"   ✅ Authenticated as: @{user.data.username}")
                else:
                    print("   ⚠️ Could not fetch user info")
            except Exception as e:
                print(f"   ❌ Authentication test failed: {e}")

        except Exception as e:
            print(f"   ❌ Failed to create API: {e}")
    else:
        print("\n2️⃣ OAuth 2.0: ❌ Missing TW_OAUTH2_ACCESS_TOKEN")

except ImportError:
    print("❌ pytwitter not installed")
    print("   Install with: uv pip install python-twitter-v2")

print("\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)

print("""
For X API v2, you need:

Option 1: OAuth 1.0a (Best for posting & reading)
  ✅ TW_CLIENT_ID (API Key / Consumer Key)
  ✅ TW_CLIENT_SECRET (API Secret / Consumer Secret)
  ✅ TW_ACCESS_TOKEN
  ✅ TW_ACCESS_SECRET

  Get these from: https://developer.twitter.com/
  → Your Project → App Settings → Keys and Tokens

Option 2: OAuth 2.0 (Newer, but may need refresh)
  ✅ TW_OAUTH2_ACCESS_TOKEN
  ✅ TW_OAUTH2_REFRESH_TOKEN (for refreshing expired tokens)

COMMON ISSUES:
1. App permissions not set correctly
   → Go to App Settings → User authentication settings
   → Enable OAuth 1.0a
   → Set permissions to "Read and Write"

2. Access Level too low
   → Make sure you have "Elevated" or "Essential" access
   → Free tier has limited endpoints

3. Tokens expired
   → Regenerate tokens in developer portal

WORKAROUND:
If credentials don't work, the tool will use MOCK MODE for testing.
You can still test the LLM comment generation and workflow logic.
""")

print("="*70)
