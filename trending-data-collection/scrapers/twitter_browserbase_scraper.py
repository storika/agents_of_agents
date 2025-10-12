#!/usr/bin/env python3
"""
Twitter Browserbase Scraper - Scrapes Twitter (X.com) trending tabs using Browserbase
and saves JSON output with timestamps.

This script scrapes multiple Twitter trending pages:
- https://x.com/explore/tabs/trending
- https://x.com/explore/tabs/news
- https://x.com/explore/tabs/sports
- https://x.com/explore/tabs/entertainment

It extracts trending topics, hashtags, and metadata, then saves to JSON.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from browserbase import Browserbase
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")

# Configuration
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")
OUTPUT_DIR = Path("../outputs/twitter_trends")

# Twitter trending URLs to scrape
TWITTER_URLS = {
    "trending": "https://x.com/explore/tabs/trending",
    "news": "https://x.com/explore/tabs/news",
    "sports": "https://x.com/explore/tabs/sports",
    "entertainment": "https://x.com/explore/tabs/entertainment"
}

# Validate credentials
if not BROWSERBASE_API_KEY or not BROWSERBASE_PROJECT_ID:
    raise ValueError("Missing BROWSERBASE_API_KEY or BROWSERBASE_PROJECT_ID in .env file")


def extract_trending_topics(page):
    """
    Extract trending topics from current Twitter page.

    Args:
        page: Playwright page object

    Returns:
        list: List of trending topics with metadata
    """
    trending_topics = []

    try:
        # Wait for content to load
        print("  Waiting for page content to load...")
        time.sleep(5)

        # Try multiple selector strategies for trending items
        # Twitter's structure: trends are usually in articles or divs with specific patterns
        selectors_to_try = [
            '[data-testid="trend"]',  # Common Twitter test ID
            'article',  # Trending items are often in article tags
            '[aria-label*="Trending"]',
            'div[data-testid*="trend"]',
        ]

        trending_elements = []
        for selector in selectors_to_try:
            try:
                elements = page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    print(f"  Found {len(elements)} elements with selector: {selector}")
                    trending_elements = elements
                    break
            except Exception as e:
                continue

        if not trending_elements:
            print("  Warning: Could not find trending elements with standard selectors")
            print("  Attempting to extract text content from page...")

            # Fallback: try to get all visible text
            try:
                page_text = page.locator('body').inner_text()
                # Save for debugging
                return [{"error": "Could not parse trending topics", "page_text_preview": page_text[:500]}]
            except:
                return [{"error": "Could not extract any content from page"}]

        # Extract data from each trending element
        for i, element in enumerate(trending_elements[:20]):  # Limit to top 20
            try:
                # Get all text content from the element
                text_content = element.inner_text()

                # Try to extract structured data
                topic = {
                    "rank": i + 1,
                    "raw_text": text_content,
                    "timestamp": datetime.now().isoformat()
                }

                # Try to parse trending topic structure
                # Typical format:
                # Category · Trending
                # #Hashtag or Topic Name
                # 123K posts
                lines = text_content.strip().split('\n')

                if len(lines) >= 2:
                    # First line is often category/metadata
                    topic["category"] = lines[0].strip() if lines[0] else None

                    # Second line is usually the topic/hashtag
                    topic["topic_name"] = lines[1].strip() if lines[1] else None

                    # Look for engagement metrics (posts, tweets count)
                    for line in lines[2:]:
                        if 'post' in line.lower() or 'tweet' in line.lower():
                            topic["post_count"] = line.strip()
                            break

                # Try to get href/link if available
                try:
                    link = element.query_selector('a')
                    if link:
                        href = link.get_attribute('href')
                        if href:
                            topic["url"] = f"https://x.com{href}" if href.startswith('/') else href
                except:
                    pass

                trending_topics.append(topic)

            except Exception as e:
                print(f"  Error extracting topic {i}: {e}")
                continue

        print(f"  Successfully extracted {len(trending_topics)} trending topics")

    except Exception as e:
        print(f"  Error in extract_trending_topics: {e}")
        import traceback
        traceback.print_exc()
        return [{"error": str(e)}]

    return trending_topics


def scrape_twitter_tab(tab_name, url, bb):
    """
    Scrape a single Twitter trending tab.

    Args:
        tab_name (str): Name of the tab (e.g., 'trending', 'news')
        url (str): URL to scrape
        bb: Browserbase client instance

    Returns:
        dict: Scraped data with metadata
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scraping {tab_name} tab...")
    print(f"  URL: {url}")

    session = None
    session_id = None

    try:
        # Create Browserbase session
        print("  Creating Browserbase session...")
        session = bb.sessions.create(
            project_id=BROWSERBASE_PROJECT_ID,
            browser_settings={
                "block_ads": True,
                "viewport": {
                    "width": 1920,
                    "height": 1080
                }
            }
        )
        session_id = session.id
        print(f"  Session created: {session_id}")

        # Connect with Playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0]

            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()

            # Navigate to Twitter
            print(f"  Navigating to URL...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Wait for page to load and Twitter content to render
            print("  Waiting for content to load...")
            time.sleep(8)  # Twitter needs time for dynamic content

            # Extract trending topics
            trending_data = extract_trending_topics(page)

            # Take a screenshot for debugging
            try:
                screenshot_path = f"debug_{tab_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=screenshot_path)
                print(f"  Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"  Could not save screenshot: {e}")

            # Close browser
            browser.close()

        return {
            "tab": tab_name,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "trending_count": len(trending_data),
            "trending_topics": trending_data,
            "success": True
        }

    except Exception as e:
        print(f"  ✗ Error scraping {tab_name}: {e}")
        import traceback
        traceback.print_exc()

        return {
            "tab": tab_name,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "error": str(e),
            "success": False
        }

    finally:
        # Close session
        if session_id:
            try:
                print(f"  Closing session {session_id}...")
            except Exception as e:
                print(f"  Warning: {e}")


def scrape_all_twitter_trends():
    """
    Scrape all Twitter trending tabs and save combined results.

    Returns:
        str: Path to saved JSON file, or None if failed
    """
    print("=" * 80)
    print("Twitter Browserbase Scraper")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scraping {len(TWITTER_URLS)} Twitter trending tabs")
    print("=" * 80)

    # Initialize Browserbase
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)

    # Scrape all tabs
    results = {}
    for tab_name, url in TWITTER_URLS.items():
        tab_data = scrape_twitter_tab(tab_name, url, bb)
        results[tab_name] = tab_data

        # Wait between requests to be respectful
        time.sleep(3)

    # Create combined output
    output = {
        "scrape_timestamp": datetime.now().isoformat(),
        "scrape_timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_tabs_scraped": len(results),
        "tabs": results,
        "summary": {
            "total_trending_topics": sum(
                tab.get("trending_count", 0)
                for tab in results.values()
                if tab.get("success")
            ),
            "successful_tabs": sum(
                1 for tab in results.values() if tab.get("success")
            ),
            "failed_tabs": sum(
                1 for tab in results.values() if not tab.get("success")
            )
        }
    }

    # Save to JSON file
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)

        filename = f"twitter_trending_browserbase_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 80)
        print("✓ SCRAPING COMPLETE")
        print("=" * 80)
        print(f"Results saved to: {filepath}")
        print(f"Total trending topics extracted: {output['summary']['total_trending_topics']}")
        print(f"Successful tabs: {output['summary']['successful_tabs']}/{len(TWITTER_URLS)}")

        return str(filepath)

    except Exception as e:
        print(f"\n✗ Error saving results: {e}")
        import traceback
        traceback.print_exc()
        return None


def scrape_once():
    """Run a single scrape (for testing)."""
    result = scrape_all_twitter_trends()

    if result:
        print("\n✓ Scrape completed successfully!")
        print(f"JSON saved to: {result}")
    else:
        print("\n✗ Scrape failed. Check the error messages above.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python twitter_browserbase_scraper.py          # Run single scrape")
        print("  python twitter_browserbase_scraper.py --help   # Show this help")
        print()
        print("The script will:")
        print("  1. Create Browserbase sessions for each Twitter tab")
        print("  2. Navigate to Twitter trending pages:")
        print("     - /explore/tabs/trending")
        print("     - /explore/tabs/news")
        print("     - /explore/tabs/sports")
        print("     - /explore/tabs/entertainment")
        print("  3. Extract trending topics and metadata")
        print("  4. Save combined results to JSON file")
        print()
        print("Output: twitter_trending_browserbase_YYYYMMDD_HHMMSS.json")
    else:
        try:
            scrape_once()
        except KeyboardInterrupt:
            print("\n\nScraper stopped by user.")
