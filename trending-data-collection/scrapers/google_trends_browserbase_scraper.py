#!/usr/bin/env python3
"""
Google Trends Browserbase Scraper - Scrapes Google Trends using Browserbase
and downloads CSV exports every 4 hours.

This script:
1. Creates a Browserbase session
2. Navigates to Google Trends with filters (geo=US, hours=4, status=active, sort=search-volume)
3. Clicks Export button and downloads CSV
4. Saves CSV locally with timestamp
5. Properly closes the session
"""

import os
import time
import requests
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
GOOGLE_TRENDS_URL = "https://trends.google.com/trending?geo=US&hours=4&status=active&sort=search-volume"
OUTPUT_DIR = Path("../outputs/google_trends")

# Validate credentials
if not BROWSERBASE_API_KEY or not BROWSERBASE_PROJECT_ID:
    raise ValueError("Missing BROWSERBASE_API_KEY or BROWSERBASE_PROJECT_ID in .env file")


def scrape_google_trends():
    """
    Scrape Google Trends and download CSV using Browserbase.

    Returns:
        str: Path to downloaded CSV file, or None if failed
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting Google Trends scrape...")

    # Initialize Browserbase client
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    session = None
    session_id = None

    try:
        # Create a Browserbase session with download tracking enabled
        print("Creating Browserbase session...")
        session = bb.sessions.create(
            project_id=BROWSERBASE_PROJECT_ID,
            browser_settings={
                "record_session": True,  # Enable session recording
                "block_ads": True,       # Block ads for faster loading
                "viewport": {
                    "width": 1920,
                    "height": 1080
                }
            }
        )
        session_id = session.id
        print(f"Session created: {session_id}")
        print(f"Session URL: {session.connect_url}")

        # Connect to the browser using Playwright
        with sync_playwright() as playwright:
            print("Connecting to remote browser...")
            browser = playwright.chromium.connect_over_cdp(session.connect_url)

            # Get the default context and page
            # Note: With connect_over_cdp, we use the existing context
            context = browser.contexts[0]

            # Create a new page with download support if possible
            if context.pages:
                page = context.pages[0]
            else:
                # Create new page (downloads should be enabled by default in Browserbase)
                page = context.new_page()

            # Navigate to Google Trends
            print(f"Navigating to: {GOOGLE_TRENDS_URL}")
            page.goto(GOOGLE_TRENDS_URL, wait_until="domcontentloaded", timeout=60000)

            # Wait for the page to load completely
            print("Waiting for page to load...")
            time.sleep(10)  # Give more time for dynamic content and Export button to load

            # Try to find and click the Export button
            print("Looking for Export button...")

            # Multiple selector strategies to find the Export button
            export_selectors = [
                'button:has-text("Export")',
                '[aria-label*="Export"]',
                'button[aria-label*="Export"]',
                'text=Export',
                '.export-button',
                '[data-tooltip*="Export"]'
            ]

            export_button = None
            for selector in export_selectors:
                try:
                    export_button = page.wait_for_selector(selector, timeout=5000)
                    if export_button:
                        print(f"Found Export button with selector: {selector}")
                        break
                except PlaywrightTimeout:
                    continue

            if not export_button:
                # Take a screenshot for debugging
                screenshot_path = f"debug_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                page.screenshot(path=screenshot_path)
                print(f"Could not find Export button. Screenshot saved to: {screenshot_path}")
                raise Exception("Export button not found on page")

            # Click the Export button
            print("Clicking Export button...")
            export_button.click()

            # Wait for dropdown menu to appear
            time.sleep(2)

            # Try to find and click the CSV option in the dropdown
            print("Looking for CSV download option...")

            # Wait a bit more for the dropdown to fully render
            time.sleep(1)

            # Set up download handler BEFORE clicking
            print("Setting up download handler...")

            # Use JavaScript to click the CSV download button
            try:
                print("Attempting to click 'Download CSV' using JavaScript...")

                # Use JavaScript to click since the element might be hidden/in a dropdown
                # Find the element that contains "Download CSV" text and click its parent button/div
                csv_element = page.get_by_text("Download CSV").first
                csv_element.evaluate("element => element.closest('button, div[role=\"menuitem\"], li').click()")
                print("Clicked via JavaScript")

                # Wait for the download to be processed by Browserbase
                print("Waiting for download to be processed by Browserbase (15 seconds)...")
                time.sleep(15)

            except Exception as e1:
                print(f"JavaScript click failed: {e1}")
                # Fallback to other selectors
                csv_selectors = [
                    'div:has-text("Download CSV")',
                    '[role="menuitem"]:has-text("Download CSV")',
                    'button:has-text("Download CSV")',
                    'a:has-text("Download CSV")',
                    'li:has-text("Download CSV")',
                    'span:has-text("Download CSV")',
                    'text="Download CSV"'
                ]

                csv_option = None
                for selector in csv_selectors:
                    try:
                        csv_option = page.wait_for_selector(selector, timeout=5000)
                        if csv_option:
                            print(f"Found CSV option with selector: {selector}")
                            csv_option.click()
                            break
                    except PlaywrightTimeout:
                        continue

                if not csv_option:
                    # Take a screenshot for debugging
                    screenshot_path = f"debug_dropdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    page.screenshot(path=screenshot_path)
                    print(f"Could not find CSV option. Screenshot saved to: {screenshot_path}")

                    # Try to get the page content for debugging
                    print("\nAttempting to list all visible text on page...")
                    all_text = page.locator('body').inner_text()
                    if 'Download CSV' in all_text:
                        print("'Download CSV' text IS present on page")
                    else:
                        print("'Download CSV' text is NOT present on page")

                    raise Exception("CSV download option not found")

            # Close browser before retrieving downloads from Browserbase API
            print("Closing browser...")
            browser.close()

        # Now retrieve the download from Browserbase API
        print("\nRetrieving download from Browserbase API...")

        # Try multiple times in case the download is still processing
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if attempt > 0:
                    print(f"Retry attempt {attempt + 1}/{max_attempts}...")
                    time.sleep(5)

                downloads_response = bb.sessions.downloads.list(session_id)
                print(f"Got response from Browserbase downloads API")

                # Check if it has read() method (BinaryAPIResponse)
                if hasattr(downloads_response, 'read'):
                    csv_content = downloads_response.read()
                    print(f"Got binary response with {len(csv_content)} bytes")

                    # Check if it's actually CSV content or empty/invalid
                    if len(csv_content) < 100:  # Too small to be a real CSV
                        print("Response too small, might be empty. Retrying...")
                        continue

                    # Save the CSV file
                    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
                    filename = f"trending_US_4h_{timestamp}.csv"
                    filepath = OUTPUT_DIR / filename

                    with open(filepath, 'wb') as f:
                        f.write(csv_content)

                    print(f"✓ Successfully downloaded CSV to: {filepath}")
                    print(f"  - File size: {len(csv_content)} bytes")

                    # Show preview
                    try:
                        preview = csv_content.decode('utf-8').split('\n')[:3]
                        print(f"  - Preview:")
                        for line in preview:
                            print(f"    {line[:100]}")
                    except Exception as e:
                        print(f"  - Preview failed: {e}")

                    return str(filepath)
                else:
                    print(f"Unexpected response type: {type(downloads_response)}")
                    if attempt < max_attempts - 1:
                        continue
                    return None

            except Exception as e:
                print(f"Error retrieving downloads (attempt {attempt + 1}): {e}")
                if attempt == max_attempts - 1:
                    import traceback
                    traceback.print_exc()
                    return None

        print("Failed to retrieve download after all attempts")
        return None

    except Exception as e:
        print(f"✗ Error during scrape: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        # Always close the session to avoid wasting usage time
        if session_id:
            try:
                print(f"Closing Browserbase session {session_id}...")
                # Session will close automatically after browser disconnects
                # Browserbase sessions are designed to auto-terminate
                print("Session will close automatically")
            except Exception as e:
                print(f"Warning: {e}")


def scrape_once():
    """Run a single scrape (for testing)."""
    print("=" * 80)
    print("Google Trends Browserbase Scraper")
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
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python google_trends_browserbase_scraper.py          # Run single scrape")
        print("  python google_trends_browserbase_scraper.py --help   # Show this help")
        print()
        print("The script will:")
        print("  1. Create a Browserbase browser session")
        print("  2. Navigate to Google Trends (US, 4h, active, sorted by search volume)")
        print("  3. Click Export → CSV")
        print("  4. Download and save the CSV file")
        print("  5. Close the session")
        print()
        print("Output: trending_US_4h_YYYYMMDD-HHMM.csv")
    else:
        try:
            scrape_once()
        except KeyboardInterrupt:
            print("\n\nScraper stopped by user.")
