"""Configuration for trend research pipeline"""

from pathlib import Path

# Directories
PROJECT_ROOT = Path(__file__).parent.parent
TREND_DATA_DIR = PROJECT_ROOT / "trend_data"
SCRAPERS_DIR = Path(__file__).parent / "scrapers"

# Ensure directories exist
TREND_DATA_DIR.mkdir(exist_ok=True)

# Schedule settings
COLLECTION_INTERVAL_HOURS = 3

# Output settings
OUTPUT_FILENAME_PATTERN = "trending_{timestamp}.json"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Scraper settings
MAX_GOOGLE_TRENDS = 25
MAX_TWITTER_TRENDS_PER_TAB = 30
MAX_POSTS_PER_KEYWORD = 10
MAX_KEYWORDS_TO_ANALYZE = 10
