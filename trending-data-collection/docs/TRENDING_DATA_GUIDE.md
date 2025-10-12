# Trending Data Collection System

Complete system for collecting and analyzing trending data from Google Trends and Twitter (X.com) every 3-4 hours.

## 🎯 What This System Does

1. **Scrapes Google Trends** - Collects trending searches in the US
2. **Scrapes Twitter Trending** - Collects trending topics from 4 Twitter tabs (trending, news, sports, entertainment)
3. **Analyzes Trending Keywords** - Searches for actual posts on X.com based on trending keywords
4. **Generates Unified JSON** - Combines all data into analyst-ready format

## 📁 Project Structure

```
.
├── google_trends_browserbase_scraper.py    # Google Trends scraper (Browserbase)
├── twitter_browserbase_scraper.py          # Twitter trending tabs scraper (NEW)
├── twitter_post_analyzer.py                # Analyzes keywords & extracts posts (NEW)
├── trending_data_pipeline.py               # Main orchestrator (NEW)
├── requirements.txt                        # Python dependencies
├── .env                                    # API keys (BROWSERBASE_API_KEY, etc.)
└── pipeline_output/                        # Final unified JSON outputs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment (if using)
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Install Playwright browsers (if not already done)
playwright install chromium
```

### 2. Run the Complete Pipeline Once

```bash
python trending_data_pipeline.py
```

This will:
- Scrape Google Trends → saves `trending_US_4h_YYYYMMDD-HHMM.csv`
- Scrape Twitter tabs → saves `twitter_trending_browserbase_YYYYMMDD_HHMMSS.json`
- Analyze keywords → saves `trending_posts_analysis_YYYYMMDD_HHMMSS.json`
- Generate final output → saves `trending_data_pipeline_YYYYMMDD_HHMMSS.json` in `pipeline_output/`

### 3. Run on Schedule (Every 4 Hours)

```bash
python trending_data_pipeline.py --schedule
```

Or with custom interval:

```bash
python trending_data_pipeline.py --schedule 3  # Every 3 hours
```

## 🔧 Running Individual Scrapers

You can also run each scraper independently:

### Google Trends Only
```bash
python google_trends_browserbase_scraper.py
```

### Twitter Trending Tabs Only
```bash
python twitter_browserbase_scraper.py
```

### Post Analysis Only (requires existing data files)
```bash
python twitter_post_analyzer.py trending_US_4h_20251011-1633.csv twitter_trends_data/twitter_trending_browserbase_20251011_160000.json
```

Or let it auto-find the latest files:
```bash
python twitter_post_analyzer.py
```

## 📊 Output Files

### 1. Google Trends CSV (`trending_US_4h_YYYYMMDD-HHMM.csv`)
Contains trending searches with search volume, categories, and related keywords.

### 2. Twitter Trending JSON (`twitter_trending_browserbase_YYYYMMDD_HHMMSS.json`)
```json
{
  "scrape_timestamp": "2025-10-11T16:00:00",
  "tabs": {
    "trending": {
      "trending_topics": [
        {
          "rank": 1,
          "topic_name": "#ExampleTrend",
          "category": "Sports · Trending",
          "post_count": "123K posts",
          "url": "https://x.com/..."
        }
      ]
    },
    "news": { ... },
    "sports": { ... },
    "entertainment": { ... }
  }
}
```

### 3. Posts Analysis JSON (`trending_posts_analysis_YYYYMMDD_HHMMSS.json`)
```json
{
  "analysis_timestamp": "2025-10-11T16:10:00",
  "results": [
    {
      "keyword": "trending keyword",
      "tavily_search": {
        "results": [ ... ]
      },
      "browserbase_search": {
        "posts": [
          {
            "content": "Post text...",
            "username": "@user",
            "likes": "1.2K",
            "url": "https://x.com/..."
          }
        ]
      }
    }
  ]
}
```

### 4. Final Pipeline Output (`trending_data_pipeline_YYYYMMDD_HHMMSS.json`)
Unified JSON combining all sources with metadata and insights:
```json
{
  "pipeline_metadata": { ... },
  "data_sources": {
    "google_trends": { "data": [...] },
    "twitter_trends": { "data": {...} },
    "trending_posts": { "data": {...} }
  },
  "pipeline_summary": {
    "successful_steps": 4,
    "duration_seconds": 120.5
  },
  "key_insights": {
    "top_google_trends": [...],
    "top_twitter_trends": [...],
    "total_posts_analyzed": 150
  }
}
```

## 🔑 Environment Variables

Required in `.env`:
```env
BROWSERBASE_API_KEY=bb_live_...
BROWSERBASE_PROJECT_ID=...
```

Tavily API key is hardcoded in scripts (update if needed):
```python
TAVILY_API_KEY = "tvly-dev-..."
```

## 🐛 Debugging

### View Screenshots
When scrapers encounter issues, they save debug screenshots:
- `debug_trending_*.png` - Twitter trending tabs
- `debug_search_*.png` - Twitter search pages
- `debug_dropdown_*.png` - Google Trends export issues
- `debug_screenshot_*.png` - General issues

### Check Logs
All scrapers print detailed logs to console. Look for:
- `✓` = Success
- `✗` = Error
- `[timestamp] [STEP]` = Pipeline progress

### Common Issues

**Issue:** "Export button not found" on Google Trends
- Google Trends UI may have changed
- Check `debug_screenshot_*.png` to see what the page looks like

**Issue:** "Trending elements not found" on Twitter
- Twitter requires login in some regions
- Try adjusting selectors in `twitter_browserbase_scraper.py`

**Issue:** "Session creation failed"
- Check Browserbase API key and project ID
- Verify Browserbase account has available sessions

## 📝 Next Steps for Your Colleague

Send them the final JSON file from `pipeline_output/` directory. It contains:
- All trending topics from Google and Twitter
- Actual posts with engagement metrics
- Metadata and timestamps
- Ready for data analysis, visualization, or reporting

## 🔄 Scheduling Options

### Option 1: Python Schedule (Built-in)
```bash
python trending_data_pipeline.py --schedule 4
```

### Option 2: Cron (Linux/Mac)
```bash
# Run every 4 hours
0 */4 * * * cd /path/to/project && source venv/bin/activate && python trending_data_pipeline.py
```

### Option 3: systemd Timer (Linux)
Create service and timer files for system-level scheduling.

### Option 4: PM2 (Node.js process manager)
```bash
pm2 start trending_data_pipeline.py --interpreter python3 --name "trending-scraper"
```

## 📞 Support

For issues or questions:
1. Check the screenshots in the project directory
2. Review error messages in console output
3. Verify `.env` credentials are correct
4. Test individual scrapers before running full pipeline

---

**Happy Trending Data Collection!** 🚀
