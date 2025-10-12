#!/usr/bin/env python3
"""
Twitter Trends Tavily Scraper - Uses Tavily API to discover trending topics from Twitter/X
without requiring browser automation or login.

This script:
1. Uses Tavily to search for trending content on x.com
2. Extracts trending topics and keywords from search results
3. Analyzes post titles and content to identify trending themes
4. Returns JSON format compatible with the pipeline
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
OUTPUT_DIR = Path(__file__).parent.parent / ".temp" / "twitter_trends"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Search queries for different categories
TRENDING_QUERIES = {
    "trending": "trending on twitter today",
    "news": "breaking news twitter trending",
    "sports": "sports trending twitter today",
    "entertainment": "entertainment viral twitter"
}


def extract_trending_topics_from_results(results: List[Dict], category: str) -> List[Dict[str, Any]]:
    """
    Extract trending topics from Tavily search results.

    Args:
        results: List of search results from Tavily
        category: Category name (trending, news, sports, entertainment)

    Returns:
        List of trending topic dictionaries
    """
    trending_topics = []

    for i, result in enumerate(results[:20]):  # Limit to top 20
        try:
            # Extract meaningful topic from title and content
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")

            # Try to extract a clean topic name from the title
            topic_name = title.split("|")[0].strip() if "|" in title else title.strip()
            topic_name = topic_name.split("-")[0].strip() if "-" in topic_name else topic_name

            # Skip if it's just the site name
            if topic_name.lower() in ["x", "twitter", ""]:
                topic_name = content.split(".")[0].strip() if content else "Untitled"

            topic = {
                "rank": i + 1,
                "topic_name": topic_name,
                "url": url,
                "category": category,
                "raw_text": f"{title}\n{content}",
                "timestamp": datetime.now().isoformat(),
                "source": "tavily"
            }

            # Try to extract engagement hints from content
            if any(word in content.lower() for word in ["trending", "viral", "popular"]):
                topic["engagement_hint"] = "high"

            trending_topics.append(topic)

        except Exception as e:
            print(f"  Error extracting topic {i}: {e}")
            continue

    return trending_topics


def scrape_twitter_category_tavily(category: str, query: str, client: TavilyClient) -> Dict[str, Any]:
    """
    Scrape a single Twitter trending category using Tavily.

    Args:
        category: Category name (e.g., 'trending', 'news')
        query: Search query for Tavily
        client: TavilyClient instance

    Returns:
        dict: Scraped data with metadata
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Searching {category} with Tavily...")
    print(f"  Query: {query}")

    try:
        # Search Tavily for trending Twitter content
        print(f"  Searching Tavily...")
        response = client.search(
            query=query,
            include_answer=False,
            search_depth="advanced",  # Use advanced for better results
            max_results=30,
            include_domains=["x.com", "twitter.com"],
            days=1  # Last 24 hours
        )

        results = response.get("results", [])
        print(f"  Found {len(results)} results from Tavily")

        # Extract trending topics
        trending_topics = extract_trending_topics_from_results(results, category)
        print(f"  Extracted {len(trending_topics)} trending topics")

        return {
            "tab": category,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "trending_count": len(trending_topics),
            "trending_topics": trending_topics,
            "success": True
        }

    except Exception as e:
        print(f"  ✗ Error searching {category}: {e}")
        import traceback
        traceback.print_exc()

        return {
            "tab": category,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "error": str(e),
            "success": False
        }


def scrape_all_twitter_trends():
    """
    Scrape all Twitter trending categories using Tavily and save combined results.

    Returns:
        str: Path to saved JSON file, or None if failed
    """
    # Validate credentials
    if not TAVILY_API_KEY:
        raise ValueError("Missing TAVILY_API_KEY in .env file")

    print("=" * 80)
    print("Twitter Tavily Scraper")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Searching {len(TRENDING_QUERIES)} Twitter trending categories")
    print("=" * 80)

    # Initialize Tavily
    client = TavilyClient(TAVILY_API_KEY)

    # Scrape all categories
    results = {}
    for category, query in TRENDING_QUERIES.items():
        category_data = scrape_twitter_category_tavily(category, query, client)
        results[category] = category_data

        # Wait between requests to be respectful
        time.sleep(2)

    # Create combined output
    output = {
        "scrape_timestamp": datetime.now().isoformat(),
        "scrape_timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_tabs_scraped": len(results),
        "method": "tavily_api",
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
        filename = f"twitter_trending_tavily_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 80)
        print("✓ SCRAPING COMPLETE")
        print("=" * 80)
        print(f"Results saved to: {filepath}")
        print(f"Total trending topics extracted: {output['summary']['total_trending_topics']}")
        print(f"Successful tabs: {output['summary']['successful_tabs']}/{len(TRENDING_QUERIES)}")

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
        print("  python twitter_trends_tavily.py          # Run single scrape")
        print("  python twitter_trends_tavily.py --help   # Show this help")
        print()
        print("The script will:")
        print("  1. Use Tavily API to search for trending topics on Twitter/X")
        print("  2. Search 4 categories: trending, news, sports, entertainment")
        print("  3. Extract trending topics and keywords")
        print("  4. Save combined results to JSON file")
        print()
        print("Output: twitter_trending_tavily_YYYYMMDD_HHMMSS.json")
    else:
        try:
            scrape_once()
        except KeyboardInterrupt:
            print("\n\nScraper stopped by user.")
