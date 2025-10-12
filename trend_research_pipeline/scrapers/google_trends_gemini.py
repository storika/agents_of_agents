#!/usr/bin/env python3
"""
Google Trends Gemini OCR Scraper - Scrapes Google Trends using Browserbase screenshot + Gemini Vision OCR.

This script:
1. Creates a Browserbase session
2. Navigates to Google Trends with filters (geo=US, hours=4, status=active, sort=search-volume)
3. Takes a screenshot of the trending topics
4. Uses Google Gemini Vision API to extract trending data via OCR
5. Converts extracted data to CSV format
6. Saves CSV locally with timestamp
"""

import os
import csv
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from browserbase import Browserbase
from playwright.sync_api import sync_playwright
from pydantic import BaseModel
from google import genai
from google.genai import types

# Load environment variables from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Configuration
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_TRENDS_URL = "https://trends.google.com/trending?geo=US&hours=4&status=active&sort=search-volume"
OUTPUT_DIR = Path(__file__).parent.parent / ".temp" / "google_trends"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Pydantic models for structured output
class TrendItem(BaseModel):
    """Single trending topic with metadata."""
    trend: str
    search_volume: str

class TrendsResponse(BaseModel):
    """Collection of trending topics."""
    trends: list[TrendItem]


def extract_trends_with_gemini(screenshot_path: str) -> List[dict]:
    """
    Use Google Gemini Vision to extract trending topics from screenshot.

    Args:
        screenshot_path: Path to screenshot image

    Returns:
        List of dicts with keys: Trends, Search volume, Explore link
    """
    try:
        print("  Analyzing screenshot with Gemini Vision...")

        # Initialize Gemini client
        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Read and encode image
        with open(screenshot_path, 'rb') as f:
            image_bytes = f.read()

        # Create prompt for Gemini
        prompt = """Analyze this Google Trends screenshot and extract ALL trending topics visible on the page.

For each trend, extract:
1. The trend name/keyword
2. The search volume (e.g., "500K+", "200K+") or "N/A" if not visible

Extract ALL visible trends in order."""

        # Generate with structured output using inline data
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/png'),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=TrendsResponse
            )
        )

        # Parse structured response (already validated by Pydantic)
        trends_response = response.parsed

        if not trends_response or not hasattr(trends_response, 'trends'):
            print("  ✗ No trends found in response")
            return []

        print(f"  ✓ Extracted {len(trends_response.trends)} trends from screenshot")

        # Convert to expected CSV format
        trends = []
        for item in trends_response.trends:
            trends.append({
                "Trends": item.trend,
                "Search volume": item.search_volume,
                "Explore link": ""  # Not extracted from screenshot
            })

        return trends

    except Exception as e:
        print(f"  ✗ Error extracting trends with Gemini: {e}")
        import traceback
        traceback.print_exc()
        return []


def scrape_google_trends():
    """
    Scrape Google Trends using Browserbase screenshot + Gemini OCR.

    Returns:
        str: Path to generated CSV file, or None if failed
    """
    # Validate credentials
    if not BROWSERBASE_API_KEY or not BROWSERBASE_PROJECT_ID:
        raise ValueError("Missing BROWSERBASE_API_KEY or BROWSERBASE_PROJECT_ID in .env file")

    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY in .env file")

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Google Trends scrape with Gemini OCR...")

    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    session = None
    session_id = None
    screenshot_path = None

    try:
        # Create Browserbase session
        print("Creating Browserbase session...")
        session = bb.sessions.create(
            project_id=BROWSERBASE_PROJECT_ID,
            browser_settings={
                "block_ads": True,
                "viewport": {"width": 1920, "height": 1080}
            }
        )
        session_id = session.id
        print(f"Session created: {session_id}")

        # Connect with Playwright
        with sync_playwright() as playwright:
            print("Connecting to remote browser...")
            browser = playwright.chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0]

            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()

            # Navigate to Google Trends
            print(f"Navigating to: {GOOGLE_TRENDS_URL}")
            page.goto(GOOGLE_TRENDS_URL, wait_until="domcontentloaded", timeout=60000)

            # Wait for page to load
            print("Waiting for page to load...")
            time.sleep(8)

            # Take screenshot
            print("Taking screenshot...")
            screenshot_path = OUTPUT_DIR / f"google_trends_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Screenshot saved: {screenshot_path}")

            browser.close()

        # Extract trends using Gemini OCR
        trends = extract_trends_with_gemini(str(screenshot_path))

        if not trends:
            print("  ✗ No trends extracted from screenshot")
            return None

        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        csv_filename = f"trending_US_4h_{timestamp}.csv"
        csv_path = OUTPUT_DIR / csv_filename

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Trends", "Search volume", "Explore link"])
            writer.writeheader()
            writer.writerows(trends)

        print(f"\n✓ Successfully saved {len(trends)} trends to: {csv_path}")
        return str(csv_path)

    except Exception as e:
        print(f"\n✗ Error scraping Google Trends: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if session_id:
            try:
                print(f"Closing Browserbase session {session_id}...")
            except:
                pass


def scrape_once():
    """Run a single scrape (for testing)."""
    result = scrape_google_trends()

    if result:
        print(f"\n✓ Scrape completed successfully!")
        print(f"CSV saved to: {result}")
    else:
        print(f"\n✗ Scrape failed. Check the error messages above.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python google_trends_gemini.py          # Run single scrape")
        print("  python google_trends_gemini.py --help   # Show this help")
        print()
        print("The script will:")
        print("  1. Navigate to Google Trends via Browserbase")
        print("  2. Take a screenshot of trending topics")
        print("  3. Use Gemini Vision API to extract trends via OCR")
        print("  4. Save extracted data to CSV file")
        print()
        print("Output: trending_US_4h_YYYYMMDD-HHMM.csv")
    else:
        try:
            scrape_once()
        except KeyboardInterrupt:
            print("\n\nScraper stopped by user.")
