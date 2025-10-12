# 🚀 Quick Start Guide

## Run the Complete System (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Run the full pipeline once
python trending_data_pipeline.py
```

This will automatically:
1. ✅ Scrape Google Trends (US, past 4 hours)
2. ✅ Scrape Twitter trending tabs (trending, news, sports, entertainment)
3. ✅ Analyze keywords and extract actual posts
4. ✅ Generate unified JSON in `pipeline_output/` directory

**Output:** `pipeline_output/trending_data_pipeline_YYYYMMDD_HHMMSS.json`

## Run on Schedule (Every 4 Hours)

```bash
python trending_data_pipeline.py --schedule
```

Or custom interval:
```bash
python trending_data_pipeline.py --schedule 3  # Every 3 hours
```

## What You Get

### Final Output File Structure
```json
{
  "pipeline_metadata": {
    "pipeline_timestamp": "2025-10-11T16:00:00",
    "pipeline_version": "1.0"
  },
  "data_sources": {
    "google_trends": {
      "trends_count": 112,
      "data": [ /* CSV data as list */ ]
    },
    "twitter_trends": {
      "data": {
        "tabs": {
          "trending": { "trending_topics": [...] },
          "news": { "trending_topics": [...] },
          "sports": { "trending_topics": [...] },
          "entertainment": { "trending_topics": [...] }
        }
      }
    },
    "trending_posts": {
      "data": {
        "results": [
          {
            "keyword": "trending topic",
            "browserbase_search": {
              "posts": [
                {
                  "content": "Post text...",
                  "username": "@user",
                  "url": "https://x.com/...",
                  "likes": "1.2K"
                }
              ]
            },
            "tavily_search": {
              "results": [ /* Links to posts */ ]
            }
          }
        ]
      }
    }
  },
  "key_insights": {
    "top_google_trends": [...],
    "top_twitter_trends": [...],
    "total_posts_analyzed": 150
  }
}
```

## Verify Setup

```bash
python test_setup.py
```

This checks:
- ✅ Python version
- ✅ All dependencies installed
- ✅ Environment variables set
- ✅ Browserbase credentials valid

## Individual Scrapers

### Google Trends Only
```bash
python google_trends_browserbase_scraper.py
# Output: trending_US_4h_YYYYMMDD-HHMM.csv
```

### Twitter Trends Only
```bash
python twitter_browserbase_scraper.py
# Output: twitter_trends_data/twitter_trending_browserbase_YYYYMMDD_HHMMSS.json
```

### Post Analysis Only
```bash
python twitter_post_analyzer.py
# Automatically finds latest Google Trends + Twitter Trends files
# Output: trending_analysis_data/trending_posts_analysis_YYYYMMDD_HHMMSS.json
```

Or specify files:
```bash
python twitter_post_analyzer.py trending_US_4h_20251011-1633.csv twitter_trends_data/twitter_trending_*.json
```

## For Your Colleague

Send them the JSON file from `pipeline_output/` directory. It contains everything they need:
- All trending topics from Google & Twitter
- Actual posts with engagement metrics
- Ready for analysis

## Troubleshooting

**Issue:** Script fails
```bash
# Check setup
python test_setup.py

# Check screenshots in project directory
ls -la debug_*.png
```

**Issue:** Twitter scraping returns empty results
- Twitter's UI may require adjustments
- Check `debug_*.png` screenshots to see what the page looks like
- May need login in some regions

**Issue:** Browserbase session errors
- Verify `.env` has correct credentials
- Check Browserbase account has available sessions

## Next Steps

Read the full guide: [TRENDING_DATA_GUIDE.md](TRENDING_DATA_GUIDE.md)

---

**That's it!** 🎉 Your trending data collection system is ready to go!
