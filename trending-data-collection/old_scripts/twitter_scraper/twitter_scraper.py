#!/usr/bin/env python3
"""
Twitter Trends Scraper - Scrapes X.com (Twitter) every 3 hours using Tavily API
and saves JSON output with timestamps.
"""

import json
import time
import schedule
from datetime import datetime
from pathlib import Path
from tavily import TavilyClient

# Configuration
API_KEY = "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"
OUTPUT_DIR = Path("twitter_trends_data")
SCRAPE_INTERVAL_HOURS = 3

# Initialize Tavily client
client = TavilyClient(API_KEY)


def scrape_twitter_trends():
    """Scrape Twitter trends and save to JSON file with timestamp."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Twitter scrape...")

    try:
        # Perform the search
        response = client.search(
            query="what are trending on x.com (twitter) for the past 3 hours?",
            include_answer="advanced",
            topic="news",
            search_depth="advanced",
            max_results=20,
            time_range="day",
            include_images=True,
            include_image_descriptions=True,
            include_raw_content="text",
            days=1,
            country="united states",
            include_domains=["x.com"]
        )

        # Add timestamp to response
        response_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            "timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": response
        }

        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(exist_ok=True)

        # Generate filename with timestamp
        filename = f"twitter_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = OUTPUT_DIR / filename

        # Save to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response_with_timestamp, f, indent=2, ensure_ascii=False)

        print(f"✓ Successfully saved to: {filepath}")
        print(f"  - Found {len(response.get('results', []))} results")
        print(f"  - Found {len(response.get('images', []))} images")

    except Exception as e:
        print(f"✗ Error during scrape: {e}")

        # Log error to file
        error_log = OUTPUT_DIR / "error_log.txt"
        with open(error_log, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] ERROR: {e}\n")


def run_scheduler():
    """Run the scraper on schedule."""
    print("=" * 60)
    print("Twitter Trends Scraper Started")
    print("=" * 60)
    print(f"Scrape interval: Every {SCRAPE_INTERVAL_HOURS} hours")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print(f"Next scrape at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Run immediately on start
    scrape_twitter_trends()

    # Schedule to run every 3 hours
    schedule.every(SCRAPE_INTERVAL_HOURS).hours.do(scrape_twitter_trends)

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def scrape_once():
    """Run a single scrape (for testing)."""
    print("Running single scrape...")
    scrape_twitter_trends()
    print("\nDone! Check the output directory for results.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once for testing
        scrape_once()
    else:
        # Run on schedule
        try:
            run_scheduler()
        except KeyboardInterrupt:
            print("\n\nScraper stopped by user.")
            print(f"Total files saved: {len(list(OUTPUT_DIR.glob('twitter_trends_*.json')))}")
