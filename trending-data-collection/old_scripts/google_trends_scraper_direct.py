#!/usr/bin/env python3
"""
Google Trends Browserbase Scraper (Direct Scraping) - Scrapes table data directly

This script scrapes Google Trends by reading the table data directly from the page
rather than using the Export button (which doesn't work reliably with Browserbase).

Usage:
    python google_trends_scraper_direct.py
"""

import os
import csv
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Configuration
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")
GOOGLE_TRENDS_URL = "https://trends.google.com/trending?geo=US&hours=4&status=active&sort=search-volume"
OUTPUT_DIR = Path(".")

# Validate credentials
if not BROWSERBASE_API_KEY or not BROWSERBASE_PROJECT_ID:
    raise ValueError("Missing BROWSERBASE_API_KEY or BROWSERBASE_PROJECT_ID in .env file")


def scrape_google_trends():
    """
    Scrape Google Trends table data directly and save to CSV.

    Returns:
        str: Path to saved CSV file, or None if failed
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Google Trends scrape...")

    # Initialize Browserbase client
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    session = None
    session_id = None

    try:
        # Create a Browserbase session
        print("Creating Browserbase session...")
        session = bb.sessions.create(
            project_id=BROWSERBASE_PROJECT_ID,
            browser_settings={
                "record_session": True,
                "block_ads": True,
                "viewport": {"width": 1920, "height": 1080}
            }
        )
        session_id = session.id
        print(f"Session created: {session_id}")

        # Connect to the browser using Playwright
        with sync_playwright() as playwright:
            print("Connecting to remote browser...")
            browser = playwright.chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            # Navigate to Google Trends
            print(f"Navigating to: {GOOGLE_TRENDS_URL}")
            page.goto(GOOGLE_TRENDS_URL, wait_until="domcontentloaded", timeout=60000)

            # Wait for the table to load
            print("Waiting for trends table to load...")
            time.sleep(10)

            # Extract data from the trends table
            print("Extracting trends data from table...")

            # Get all trend rows
            trends_data = []

            # Try to find trend rows - Google Trends uses various selectors
            try:
                # Wait for the table/list to be visible
                page.wait_for_selector('tr, [role="row"]', timeout=10000)

                # Get all rows (skip header if present)
                rows = page.query_selector_all('tbody tr, [role="rowgroup"] [role="row"]')

                print(f"Found {len(rows)} trend rows")

                for idx, row in enumerate(rows):
                    try:
                        # Get all cells in the row
                        cells = row.query_selector_all('td, [role="cell"]')

                        if len(cells) < 3:
                            print(f"Row {idx}: Not enough cells ({len(cells)}), skipping")
                            continue

                        # The first cell might be a checkbox, so let's find the trend name
                        # Usually in column 1 or 2
                        trend_text = ""
                        for cell_idx in range(min(3, len(cells))):
                            text = cells[cell_idx].inner_text().strip()
                            # Look for text that's not just numbers/symbols
                            if text and not text.startswith('arrow_') and len(text) > 2:
                                if not trend_text:  # First substantial text is likely the trend
                                    trend_text = text.split('\n')[0]  # Take first line only
                                    break

                        if not trend_text:
                            continue

                        # Extract search volume (usually has "K+" or numbers)
                        volume = "N/A"
                        for cell in cells:
                            text = cell.inner_text().strip()
                            if 'K+' in text or '+' in text:
                                # Extract just the volume part (first line)
                                volume = text.split('\n')[0]
                                break

                        # Extract started time
                        started = ""
                        for cell in cells:
                            text = cell.inner_text().strip()
                            if 'ago' in text or 'Active' in text:
                                # Get the time part
                                lines = text.split('\n')
                                for line in lines:
                                    if 'ago' in line:
                                        started = line
                                        break
                                break

                        # Extract trend breakdown (related terms)
                        breakdown = ""
                        # Usually in the last substantial cell
                        if len(cells) >= 4:
                            breakdown_text = cells[-1].inner_text().strip()
                            # Filter out UI elements
                            if not any(x in breakdown_text for x in ['arrow_', 'trending_up', 'Active']):
                                breakdown = breakdown_text.replace('\n', ',')[:200]  # Limit length

                        trends_data.append({
                            "Trends": trend_text,
                            "Search volume": volume,
                            "Started": started,
                            "Ended": "",
                            "Trend breakdown": breakdown,
                            "Explore link": f"https://trends.google.com/trends/explore?q={trend_text.replace(' ', '%20')}&geo=US&hl=en-US"
                        })

                    except Exception as e:
                        print(f"Error extracting row data: {e}")
                        continue

            except Exception as e:
                print(f"Error finding table rows: {e}")

                # Fallback: Try to get any visible trend text
                print("Attempting fallback scraping method...")
                trend_elements = page.query_selector_all('div:has-text("football"), div:has-text("vs"), div:has-text("sub-20")')  # Common trend patterns
                print(f"Found {len(trend_elements)} potential trend elements via fallback")

            # Close browser
            print("Closing browser...")
            browser.close()

            # Save to CSV
            if trends_data:
                timestamp = datetime.now().strftime('%Y%m%d-%H%M')
                filename = f"trending_US_4h_{timestamp}.csv"
                filepath = OUTPUT_DIR / filename

                print(f"Saving {len(trends_data)} trends to CSV...")
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ["Trends", "Search volume", "Started", "Ended", "Trend breakdown", "Explore link"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)

                    writer.writeheader()
                    for trend in trends_data:
                        writer.writerow(trend)

                print(f"✓ Successfully saved CSV to: {filepath}")
                print(f"  - Number of trends: {len(trends_data)}")

                # Show preview
                print(f"  - Preview of first 3 trends:")
                for i, trend in enumerate(trends_data[:3]):
                    print(f"    {i+1}. {trend['Trends']} - {trend['Search volume']}")

                return str(filepath)
            else:
                print("✗ No trends data extracted")
                return None

    except Exception as e:
        print(f"✗ Error during scrape: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if session_id:
            print("Session will close automatically")


def main():
    print("=" * 80)
    print("Google Trends Direct Scraper (Browserbase)")
    print("=" * 80)
    print(f"Target URL: {GOOGLE_TRENDS_URL}")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print("=" * 80)

    result = scrape_google_trends()

    if result:
        print("\n✓ Scrape completed successfully!")
        print(f"CSV saved to: {result}")
    else:
        print("\n✗ Scrape failed. Check the error messages above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScraper stopped by user.")
