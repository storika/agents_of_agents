#!/usr/bin/env python3
"""
Trending Data Pipeline - Orchestrates all scrapers to collect comprehensive trending data.

This pipeline:
1. Scrapes Google Trends (Browserbase) for trending searches
2. Scrapes Twitter trending tabs (Browserbase) for trending topics
3. Supplements with Tavily searches for additional context
4. Analyzes trending keywords and extracts actual posts
5. Generates a unified JSON output ready for analysis
6. Saves to trend_data/ directory with timestamp
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add scrapers directory to path
sys.path.insert(0, str(Path(__file__).parent / "scrapers"))

# Import our custom scrapers
import google_trends as google_scraper
import twitter_trends as twitter_scraper
import post_analyzer

# Import config
from config import (
    TREND_DATA_DIR,
    OUTPUT_FILENAME_PATTERN,
    TIMESTAMP_FORMAT,
    MAX_KEYWORDS_TO_ANALYZE
)


class TrendingDataPipeline:
    """Main pipeline orchestrator for trending data collection."""

    def __init__(self):
        self.output_dir = TREND_DATA_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.run_timestamp = None
        self.results = {}

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

    def run_pipeline(self) -> Optional[str]:
        """
        Execute the complete trending data pipeline.

        Returns:
            str: Path to final output JSON, or None if failed
        """
        self.run_timestamp = datetime.now()
        self.results = {
            "pipeline_start": self.run_timestamp.isoformat(),
            "pipeline_start_readable": self.run_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "steps": {},
            "errors": []
        }

        print("\n" + "=" * 100)
        print(" " * 35 + "TRENDING DATA PIPELINE")
        print("=" * 100)
        self.log(f"Pipeline started at {self.run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)

        # Step 1: Scrape Google Trends
        google_csv = self._step_google_trends()

        # Step 2: Scrape Twitter Trending Tabs
        twitter_json = self._step_twitter_trends()

        # Step 3: Analyze and Extract Posts
        posts_json = self._step_analyze_posts(google_csv, twitter_json)

        # Step 4: Generate Final Output
        final_output = self._step_generate_final_output(google_csv, twitter_json, posts_json)

        # Complete
        self.results["pipeline_end"] = datetime.now().isoformat()
        self.results["pipeline_duration_seconds"] = (datetime.now() - self.run_timestamp).total_seconds()

        print("\n" + "=" * 100)
        if final_output:
            self.log("✓ PIPELINE COMPLETED SUCCESSFULLY", "SUCCESS")
            print("=" * 100)
            print(f"Final output saved to: {final_output}")
            print(f"Pipeline duration: {self.results['pipeline_duration_seconds']:.1f} seconds")
            print("=" * 100)
        else:
            self.log("✗ PIPELINE FAILED", "ERROR")
            print("=" * 100)
            print("Check error messages above for details.")
            print("=" * 100)

        return final_output

    def _step_google_trends(self) -> Optional[str]:
        """
        Step 1: Scrape Google Trends.

        Returns:
            str: Path to Google Trends CSV file, or None if failed
        """
        print("\n" + "-" * 100)
        self.log("STEP 1/4: Scraping Google Trends", "STEP")
        print("-" * 100)

        try:
            csv_path = google_scraper.scrape_google_trends()

            if csv_path:
                self.log(f"✓ Google Trends scraped successfully: {csv_path}", "SUCCESS")
                self.results["steps"]["google_trends"] = {
                    "success": True,
                    "output_file": csv_path,
                    "timestamp": datetime.now().isoformat()
                }
                return csv_path
            else:
                self.log("✗ Google Trends scraping failed", "ERROR")
                self.results["steps"]["google_trends"] = {
                    "success": False,
                    "error": "Scraping returned None",
                    "timestamp": datetime.now().isoformat()
                }
                self.results["errors"].append("Google Trends scraping failed")
                return None

        except Exception as e:
            self.log(f"✗ Error in Google Trends step: {e}", "ERROR")
            self.results["steps"]["google_trends"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["errors"].append(f"Google Trends error: {e}")
            return None

    def _step_twitter_trends(self) -> Optional[str]:
        """
        Step 2: Scrape Twitter trending tabs.

        Returns:
            str: Path to Twitter trends JSON file, or None if failed
        """
        print("\n" + "-" * 100)
        self.log("STEP 2/4: Scraping Twitter Trending Tabs", "STEP")
        print("-" * 100)

        try:
            json_path = twitter_scraper.scrape_all_twitter_trends()

            if json_path:
                self.log(f"✓ Twitter trends scraped successfully: {json_path}", "SUCCESS")
                self.results["steps"]["twitter_trends"] = {
                    "success": True,
                    "output_file": json_path,
                    "timestamp": datetime.now().isoformat()
                }
                return json_path
            else:
                self.log("✗ Twitter trends scraping failed", "ERROR")
                self.results["steps"]["twitter_trends"] = {
                    "success": False,
                    "error": "Scraping returned None",
                    "timestamp": datetime.now().isoformat()
                }
                self.results["errors"].append("Twitter trends scraping failed")
                return None

        except Exception as e:
            self.log(f"✗ Error in Twitter trends step: {e}", "ERROR")
            self.results["steps"]["twitter_trends"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["errors"].append(f"Twitter trends error: {e}")
            return None

    def _step_analyze_posts(self, google_csv: Optional[str], twitter_json: Optional[str]) -> Optional[str]:
        """
        Step 3: Analyze trending keywords and extract posts.

        Args:
            google_csv: Path to Google Trends CSV
            twitter_json: Path to Twitter trends JSON

        Returns:
            str: Path to posts analysis JSON file, or None if failed
        """
        print("\n" + "-" * 100)
        self.log("STEP 3/4: Analyzing Trending Keywords & Extracting Posts", "STEP")
        print("-" * 100)

        if not google_csv and not twitter_json:
            self.log("✗ No input files available for post analysis", "ERROR")
            self.results["steps"]["post_analysis"] = {
                "success": False,
                "error": "No input files available",
                "timestamp": datetime.now().isoformat()
            }
            self.results["errors"].append("Post analysis skipped - no input files")
            return None

        try:
            posts_json = post_analyzer.analyze_trending_keywords(
                google_trends_csv=google_csv,
                twitter_trends_json=twitter_json,
                max_keywords=MAX_KEYWORDS_TO_ANALYZE
            )

            if posts_json:
                self.log(f"✓ Post analysis completed successfully: {posts_json}", "SUCCESS")
                self.results["steps"]["post_analysis"] = {
                    "success": True,
                    "output_file": posts_json,
                    "timestamp": datetime.now().isoformat()
                }
                return posts_json
            else:
                self.log("✗ Post analysis failed", "ERROR")
                self.results["steps"]["post_analysis"] = {
                    "success": False,
                    "error": "Analysis returned None",
                    "timestamp": datetime.now().isoformat()
                }
                self.results["errors"].append("Post analysis failed")
                return None

        except Exception as e:
            self.log(f"✗ Error in post analysis step: {e}", "ERROR")
            self.results["steps"]["post_analysis"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["errors"].append(f"Post analysis error: {e}")
            return None

    def _step_generate_final_output(
        self,
        google_csv: Optional[str],
        twitter_json: Optional[str],
        posts_json: Optional[str]
    ) -> Optional[str]:
        """
        Step 4: Generate unified final output JSON and save to trend_data/.

        Args:
            google_csv: Path to Google Trends CSV
            twitter_json: Path to Twitter trends JSON
            posts_json: Path to posts analysis JSON

        Returns:
            str: Path to final output JSON in trend_data/
        """
        print("\n" + "-" * 100)
        self.log("STEP 4/4: Generating Final Unified Output", "STEP")
        print("-" * 100)

        try:
            # Load data from each file
            google_data = self._load_csv_as_dict(google_csv) if google_csv else None
            twitter_data = self._load_json(twitter_json) if twitter_json else None
            posts_data = self._load_json(posts_json) if posts_json else None

            # Create unified output
            final_output = {
                "pipeline_metadata": {
                    "pipeline_timestamp": self.run_timestamp.isoformat(),
                    "pipeline_timestamp_readable": self.run_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "pipeline_version": "1.0",
                    "pipeline_description": "Comprehensive trending data collection from Google Trends and Twitter",
                    "collection_interval_hours": 3
                },
                "data_sources": {
                    "google_trends": {
                        "collected": google_csv is not None,
                        "file": google_csv,
                        "trends_count": len(google_data) if google_data else 0,
                        "data": google_data
                    },
                    "twitter_trends": {
                        "collected": twitter_json is not None,
                        "file": twitter_json,
                        "data": twitter_data
                    },
                    "trending_posts": {
                        "collected": posts_json is not None,
                        "file": posts_json,
                        "data": posts_data
                    }
                },
                "pipeline_summary": {
                    "total_steps": 4,
                    "successful_steps": sum(
                        1 for step in self.results.get("steps", {}).values()
                        if step.get("success")
                    ),
                    "failed_steps": len(self.results.get("errors", [])),
                    "errors": self.results.get("errors", []),
                    "duration_seconds": (datetime.now() - self.run_timestamp).total_seconds()
                },
                "key_insights": self._generate_insights(google_data, twitter_data, posts_data)
            }

            # Save to trend_data/ with timestamp
            timestamp_str = self.run_timestamp.strftime(TIMESTAMP_FORMAT)
            filename = OUTPUT_FILENAME_PATTERN.format(timestamp=timestamp_str)
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)

            self.log(f"✓ Final output generated: {filepath}", "SUCCESS")
            self.results["steps"]["final_output"] = {
                "success": True,
                "output_file": str(filepath),
                "timestamp": datetime.now().isoformat()
            }

            return str(filepath)

        except Exception as e:
            self.log(f"✗ Error generating final output: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            self.results["steps"]["final_output"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return None

    def _load_csv_as_dict(self, csv_path: str) -> list:
        """Load CSV file as list of dictionaries."""
        import csv
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            self.log(f"Error loading CSV {csv_path}: {e}", "WARNING")
            return []

    def _load_json(self, json_path: str) -> dict:
        """Load JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading JSON {json_path}: {e}", "WARNING")
            return {}

    def _generate_insights(self, google_data, twitter_data, posts_data) -> Dict[str, Any]:
        """Generate key insights from collected data."""
        insights = {
            "top_google_trends": [],
            "top_twitter_trends": [],
            "most_discussed_keywords": [],
            "total_posts_analyzed": 0
        }

        try:
            # Top Google Trends
            if google_data and len(google_data) > 0:
                insights["top_google_trends"] = [
                    {
                        "keyword": item.get("Trends", ""),
                        "search_volume": item.get("Search volume", "")
                    }
                    for item in google_data[:5]
                ]

            # Top Twitter Trends
            if twitter_data and "tabs" in twitter_data:
                twitter_topics = []
                for tab_name, tab_data in twitter_data["tabs"].items():
                    if tab_data.get("success"):
                        for topic in tab_data.get("trending_topics", [])[:3]:
                            twitter_topics.append({
                                "keyword": topic.get("topic_name", ""),
                                "tab": tab_name,
                                "post_count": topic.get("post_count", "")
                            })
                insights["top_twitter_trends"] = twitter_topics[:10]

            # Posts analysis summary
            if posts_data and "summary" in posts_data:
                insights["total_posts_analyzed"] = posts_data["summary"].get("total_posts_extracted", 0)
                insights["keywords_analyzed"] = posts_data["summary"].get("total_keywords_analyzed", 0)

        except Exception as e:
            self.log(f"Error generating insights: {e}", "WARNING")

        return insights


def run_pipeline_once():
    """Run the pipeline once."""
    pipeline = TrendingDataPipeline()
    result = pipeline.run_pipeline()

    if result:
        print(f"\n✓ Pipeline completed successfully!")
        print(f"   Output: {result}")
        return 0
    else:
        print(f"\n✗ Pipeline failed!")
        return 1


def main():
    """Main entry point."""
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        print("\nUsage:")
        print("  python pipeline.py              Run pipeline once")
        print("  python pipeline.py --help       Show this help")
        return

    # Run once
    exit_code = run_pipeline_once()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
