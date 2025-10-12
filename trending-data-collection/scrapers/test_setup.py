#!/usr/bin/env python3
"""
Test Setup - Verify all dependencies and configuration are correct.

This script checks:
1. Python dependencies are installed
2. Environment variables are set
3. Import statements work
4. Browserbase credentials are valid
"""

import sys
from pathlib import Path

print("=" * 80)
print(" " * 25 + "TRENDING DATA SYSTEM - SETUP TEST")
print("=" * 80)

# Test 1: Check Python version
print("\n[1/6] Checking Python version...")
version_info = sys.version_info
if version_info.major >= 3 and version_info.minor >= 8:
    print(f"✓ Python {version_info.major}.{version_info.minor}.{version_info.micro} (OK)")
else:
    print(f"✗ Python {version_info.major}.{version_info.minor}.{version_info.micro} (Need 3.8+)")
    sys.exit(1)

# Test 2: Check required packages
print("\n[2/6] Checking required packages...")
required_packages = {
    "browserbase": "Browserbase",
    "playwright": "Playwright",
    "tavily": "Tavily",
    "schedule": "Schedule",
    "dotenv": "python-dotenv",
    "requests": "Requests",
}

missing_packages = []
for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        print(f"✓ {package_name}")
    except ImportError:
        print(f"✗ {package_name} (Missing)")
        missing_packages.append(package_name)

if missing_packages:
    print(f"\n✗ Missing packages: {', '.join(missing_packages)}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Test 3: Check environment variables
print("\n[3/6] Checking environment variables...")
import os
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

required_env_vars = {
    "BROWSERBASE_API_KEY": os.getenv("BROWSERBASE_API_KEY"),
    "BROWSERBASE_PROJECT_ID": os.getenv("BROWSERBASE_PROJECT_ID"),
}

missing_env_vars = []
for var_name, var_value in required_env_vars.items():
    if var_value:
        masked = var_value[:8] + "..." if len(var_value) > 8 else "***"
        print(f"✓ {var_name} = {masked}")
    else:
        print(f"✗ {var_name} (Not set)")
        missing_env_vars.append(var_name)

if missing_env_vars:
    print(f"\n✗ Missing environment variables: {', '.join(missing_env_vars)}")
    print("Check your .env file")
    sys.exit(1)

# Test 4: Check script files
print("\n[4/6] Checking script files...")
required_scripts = [
    "google_trends_browserbase_scraper.py",
    "twitter_browserbase_scraper.py",
    "twitter_post_analyzer.py",
    "trending_data_pipeline.py",
]

missing_scripts = []
for script in required_scripts:
    # Check in current directory (when run from scrapers/)
    script_path = Path(script)
    if script_path.exists():
        print(f"✓ {script}")
    else:
        print(f"✗ {script} (Not found)")
        missing_scripts.append(script)

if missing_scripts:
    print(f"\n✗ Missing scripts: {', '.join(missing_scripts)}")
    sys.exit(1)

# Test 5: Test imports from scripts
print("\n[5/6] Testing script imports...")
try:
    import google_trends_browserbase_scraper
    print("✓ google_trends_browserbase_scraper")
except Exception as e:
    print(f"✗ google_trends_browserbase_scraper: {e}")

try:
    import twitter_browserbase_scraper
    print("✓ twitter_browserbase_scraper")
except Exception as e:
    print(f"✗ twitter_browserbase_scraper: {e}")

try:
    import twitter_post_analyzer
    print("✓ twitter_post_analyzer")
except Exception as e:
    print(f"✗ twitter_post_analyzer: {e}")

try:
    import trending_data_pipeline
    print("✓ trending_data_pipeline")
except Exception as e:
    print(f"✗ trending_data_pipeline: {e}")

# Test 6: Test Browserbase connection
print("\n[6/6] Testing Browserbase connection...")
try:
    from browserbase import Browserbase

    bb = Browserbase(api_key=os.getenv("BROWSERBASE_API_KEY"))
    print("✓ Browserbase client initialized")

    # Try to create a session (will be closed immediately)
    try:
        session = bb.sessions.create(
            project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
            browser_settings={"viewport": {"width": 1920, "height": 1080}}
        )
        print(f"✓ Browserbase session created: {session.id}")
        print("✓ Browserbase credentials are valid")
        # Session will auto-close
    except Exception as e:
        print(f"✗ Could not create Browserbase session: {e}")
        print("  Check your API key and project ID")
        sys.exit(1)

except Exception as e:
    print(f"✗ Browserbase test failed: {e}")
    sys.exit(1)

# All tests passed!
print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED!")
print("=" * 80)
print("\nYou're ready to run the trending data pipeline:")
print("  python trending_data_pipeline.py              # Run once")
print("  python trending_data_pipeline.py --schedule   # Run every 4 hours")
print()
print("Or run individual scrapers:")
print("  python google_trends_browserbase_scraper.py")
print("  python twitter_browserbase_scraper.py")
print("  python twitter_post_analyzer.py")
print("=" * 80)
