#!/usr/bin/env python3
"""
Twitter Post Analyzer - Analyzes trending keywords and extracts actual trending posts.

This script:
1. Reads trending keywords from Google Trends CSV and Twitter Tavily JSON
2. Uses Tavily to search for posts about those keywords on x.com
3. Extracts post content, engagement metrics, and metadata
4. Saves structured JSON output for analysis
"""

import os
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
# Intermediate files saved to temp location (not trend_data/)
OUTPUT_DIR = Path(__file__).parent.parent / ".temp" / "post_analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Note: Credentials are validated when analyze functions are called
# Not at import time to allow module inspection without .env


def read_google_trends_keywords(csv_path: str) -> List[Dict[str, Any]]:
    """
    Read trending keywords from Google Trends CSV file.

    Args:
        csv_path (str): Path to Google Trends CSV file

    Returns:
        List[Dict]: List of trending keywords with metadata
    """
    keywords = []

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                keywords.append({
                    "keyword": row.get("Trends", ""),
                    "search_volume": row.get("Search volume", ""),
                    "source": "google_trends",
                    "explore_link": row.get("Explore link", "")
                })

        print(f"✓ Read {len(keywords)} keywords from Google Trends CSV")
        return keywords

    except Exception as e:
        print(f"✗ Error reading Google Trends CSV: {e}")
        return []


def read_twitter_trends_keywords(json_path: str) -> List[Dict[str, Any]]:
    """
    Read trending keywords from Twitter Browserbase JSON file.

    Args:
        json_path (str): Path to Twitter trending JSON file

    Returns:
        List[Dict]: List of trending keywords with metadata
    """
    keywords = []

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract keywords from all tabs
        for tab_name, tab_data in data.get("tabs", {}).items():
            if not tab_data.get("success"):
                continue

            for topic in tab_data.get("trending_topics", []):
                keywords.append({
                    "keyword": topic.get("topic_name", topic.get("raw_text", "")),
                    "category": topic.get("category", ""),
                    "post_count": topic.get("post_count", ""),
                    "tab": tab_name,
                    "source": "twitter_trending",
                    "url": topic.get("url", "")
                })

        print(f"✓ Read {len(keywords)} keywords from Twitter Trending JSON")
        return keywords

    except Exception as e:
        print(f"✗ Error reading Twitter Trending JSON: {e}")
        return []


def search_twitter_posts_tavily(keyword: str, client: TavilyClient) -> Dict[str, Any]:
    """
    Search for Twitter posts about a keyword using Tavily.

    Args:
        keyword (str): Search keyword
        client: TavilyClient instance

    Returns:
        Dict: Search results from Tavily
    """
    try:
        print(f"  Searching Tavily for: {keyword}")

        response = client.search(
            query=f"{keyword} site:x.com OR site:twitter.com",
            include_answer=False,
            search_depth="basic",
            max_results=10,
            include_domains=["x.com", "twitter.com"],
            days=1
        )

        results = response.get("results", [])
        print(f"  Found {len(results)} results from Tavily")

        return {
            "keyword": keyword,
            "source": "tavily",
            "results_count": len(results),
            "results": results
        }

    except Exception as e:
        print(f"  ✗ Error searching Tavily for '{keyword}': {e}")
        return {
            "keyword": keyword,
            "source": "tavily",
            "error": str(e),
            "results_count": 0,
            "results": []
        }


def analyze_trending_keywords(
    google_trends_csv: str = None,
    twitter_trends_json: str = None,
    max_keywords: int = 10
) -> str:
    """
    Analyze trending keywords and extract posts.

    Args:
        google_trends_csv (str): Path to Google Trends CSV
        twitter_trends_json (str): Path to Twitter Trending JSON
        max_keywords (int): Maximum number of keywords to analyze

    Returns:
        str: Path to output JSON file
    """
    # Validate credentials
    if not TAVILY_API_KEY:
        raise ValueError("Missing TAVILY_API_KEY in .env file")

    print("=" * 80)
    print("Twitter Post Analyzer (Tavily)")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Collect keywords from all sources
    all_keywords = []

    if google_trends_csv and Path(google_trends_csv).exists():
        print(f"\nReading Google Trends: {google_trends_csv}")
        all_keywords.extend(read_google_trends_keywords(google_trends_csv))

    if twitter_trends_json and Path(twitter_trends_json).exists():
        print(f"\nReading Twitter Trends: {twitter_trends_json}")
        all_keywords.extend(read_twitter_trends_keywords(twitter_trends_json))

    if not all_keywords:
        print("\n✗ No keywords found. Please provide valid input files.")
        return None

    print(f"\nTotal keywords collected: {len(all_keywords)}")

    # Deduplicate and limit keywords
    seen_keywords = set()
    unique_keywords = []
    for kw in all_keywords:
        keyword_text = kw.get("keyword", "").strip().lower()
        if keyword_text and keyword_text not in seen_keywords:
            seen_keywords.add(keyword_text)
            unique_keywords.append(kw)

    keywords_to_analyze = unique_keywords[:max_keywords]
    print(f"Analyzing top {len(keywords_to_analyze)} unique keywords")

    # Initialize Tavily client
    tavily_client = TavilyClient(TAVILY_API_KEY)

    # Analyze each keyword
    results = []

    for i, kw_data in enumerate(keywords_to_analyze):
        keyword = kw_data.get("keyword", "")
        print(f"\n[{i+1}/{len(keywords_to_analyze)}] Analyzing: {keyword}")

        # Search with Tavily only
        tavily_results = search_twitter_posts_tavily(keyword, tavily_client)

        # Store results
        combined = {
            "keyword": keyword,
            "keyword_metadata": kw_data,
            "tavily_search": tavily_results,
            "total_posts_found": tavily_results.get("results_count", 0)
        }

        results.append(combined)

        # Wait between keywords to avoid rate limits
        time.sleep(2)

    # Create output
    output = {
        "analysis_timestamp": datetime.now().isoformat(),
        "analysis_timestamp_readable": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "keywords_analyzed": len(results),
        "input_files": {
            "google_trends_csv": google_trends_csv,
            "twitter_trends_json": twitter_trends_json
        },
        "results": results,
        "summary": {
            "total_keywords_analyzed": len(results),
            "total_posts_extracted": sum(r.get("total_posts_found", 0) for r in results),
            "tavily_results": sum(r.get("tavily_search", {}).get("results_count", 0) for r in results)
        }
    }

    # Save to JSON
    try:
        filename = f"trending_posts_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 80)
        print("✓ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"Results saved to: {filepath}")
        print(f"Keywords analyzed: {output['summary']['total_keywords_analyzed']}")
        print(f"Total posts extracted: {output['summary']['total_posts_extracted']}")
        print(f"  - Tavily results: {output['summary']['tavily_results']}")

        return str(filepath)

    except Exception as e:
        print(f"\n✗ Error saving results: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function for command-line usage."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python twitter_post_analyzer.py [google_trends.csv] [twitter_trends.json]")
        print()
        print("Arguments:")
        print("  google_trends.csv       - Path to Google Trends CSV file (optional)")
        print("  twitter_trends.json     - Path to Twitter Browserbase JSON file (optional)")
        print()
        print("The script will:")
        print("  1. Read trending keywords from input files")
        print("  2. Search for posts using Tavily API")
        print("  3. Scrape Twitter search results with Browserbase")
        print("  4. Extract post content and engagement metrics")
        print("  5. Save combined results to JSON")
        print()
        print("Output: trending_posts_analysis_YYYYMMDD_HHMMSS.json")
        return

    # Get file paths from command line or find latest files
    google_csv = None
    twitter_json = None

    if len(sys.argv) > 1:
        google_csv = sys.argv[1]

    if len(sys.argv) > 2:
        twitter_json = sys.argv[2]

    # If not provided, find latest files
    if not google_csv:
        csv_files = sorted(Path("../outputs/google_trends").glob("trending_US_4h_*.csv"), reverse=True)
        if csv_files:
            google_csv = str(csv_files[0])
            print(f"Using latest Google Trends CSV: {google_csv}")

    if not twitter_json:
        json_files = sorted(Path("../outputs/twitter_trends").glob("twitter_trending_browserbase_*.json"), reverse=True)
        if json_files:
            twitter_json = str(json_files[0])
            print(f"Using latest Twitter Trends JSON: {twitter_json}")

    if not google_csv and not twitter_json:
        print("✗ No input files found. Please provide at least one input file.")
        print("Run with --help for usage information.")
        return

    try:
        result = analyze_trending_keywords(
            google_trends_csv=google_csv,
            twitter_trends_json=twitter_json,
            max_keywords=10
        )

        if result:
            print("\n✓ Analysis completed successfully!")
            print(f"Results saved to: {result}")
        else:
            print("\n✗ Analysis failed.")

    except KeyboardInterrupt:
        print("\n\nAnalysis stopped by user.")


if __name__ == "__main__":
    main()
