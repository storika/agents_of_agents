"""
Refresh OAuth 2.0 Access Token for Twitter API
"""

import os
import requests
import base64
from dotenv import load_dotenv, set_key

load_dotenv()

print("=" * 70)
print("Refreshing OAuth 2.0 Access Token")
print("=" * 70)

# Get credentials
CLIENT_ID = os.getenv("TW_CLIENT_ID")
CLIENT_SECRET = os.getenv("TW_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("TW_OAUTH2_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    print("❌ Missing required credentials:")
    print(f"   TW_CLIENT_ID: {'✅' if CLIENT_ID else '❌'}")
    print(f"   TW_CLIENT_SECRET: {'✅' if CLIENT_SECRET else '❌'}")
    print(f"   TW_OAUTH2_REFRESH_TOKEN: {'✅' if REFRESH_TOKEN else '❌'}")
    exit(1)

print("\n✅ All credentials found")
print(f"   CLIENT_ID: {CLIENT_ID[:10]}...")
print(f"   REFRESH_TOKEN: {REFRESH_TOKEN[:20]}...")

# Prepare OAuth 2.0 token refresh request
print("\n[Step 1] Refreshing access token...")

token_url = "https://api.twitter.com/2/oauth2/token"

# Create Basic Auth header
auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
b64_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Authorization": f"Basic {b64_auth}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN,
    "client_id": CLIENT_ID
}

try:
    response = requests.post(token_url, headers=headers, data=data, timeout=10)

    if response.status_code == 200:
        token_data = response.json()

        new_access_token = token_data.get("access_token")
        new_refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")

        if not new_access_token:
            print("❌ No access token in response")
            print(f"   Response: {token_data}")
            exit(1)

        print(f"✅ Successfully refreshed token!")
        print(f"   New access token: {new_access_token[:20]}...")
        print(f"   Expires in: {expires_in} seconds ({expires_in // 3600} hours)")

        if new_refresh_token:
            print(f"   New refresh token: {new_refresh_token[:20]}...")
        else:
            print(f"   No new refresh token (will reuse existing one)")

        # Update .env file
        print("\n[Step 2] Updating .env file...")
        env_path = ".env"

        set_key(env_path, "TW_OAUTH2_ACCESS_TOKEN", new_access_token)
        print(f"✅ Updated TW_OAUTH2_ACCESS_TOKEN")

        if new_refresh_token:
            set_key(env_path, "TW_OAUTH2_REFRESH_TOKEN", new_refresh_token)
            print(f"✅ Updated TW_OAUTH2_REFRESH_TOKEN")

        print("\n" + "=" * 70)
        print("✅ Token refresh complete!")
        print("=" * 70)
        print("\nYou can now use the agents to post to Twitter/X")
        print("The new token will expire in about", expires_in // 3600, "hours")

    else:
        print(f"❌ Token refresh failed")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code == 400:
            print("\n   Common causes:")
            print("   - Refresh token has expired")
            print("   - Invalid client credentials")
            print("   - App doesn't have OAuth 2.0 enabled")
            print("\n   Solution: Run oauth2_setup.py to get a new token set")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
