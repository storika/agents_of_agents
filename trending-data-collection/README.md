# 📊 Trending Data Collection System

> **Automated system to collect and analyze trending data from Google Trends and Twitter (X.com) every 3-4 hours**

This system scrapes trending topics, analyzes keywords, and extracts actual posts with engagement metrics—delivering analyst-ready JSON outputs.

---

## 🎯 What This System Does

1. **Scrapes Google Trends** → Top trending searches in the US (past 4 hours)
2. **Scrapes Twitter Trending Tabs** → Trending topics from 4 categories (trending, news, sports, entertainment)
3. **Analyzes Keywords** → Searches for actual posts on X.com based on trending keywords
4. **Generates Unified JSON** → Combines all data with insights for analysis

---

## 📁 Project Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env                               # Environment variables (API keys)
│
├── scrapers/                          # Main scraper scripts
│   ├── trending_data_pipeline.py     # 🚀 MAIN SCRIPT - Run this!
│   ├── google_trends_browserbase_scraper.py
│   ├── twitter_browserbase_scraper.py
│   ├── twitter_post_analyzer.py
│   └── test_setup.py                 # Setup verification
│
├── outputs/                           # All output files
│   ├── pipeline_results/             # Final unified JSON outputs ⭐
│   ├── google_trends/                # Google Trends CSV files
│   ├── twitter_trends/               # Twitter trending JSON files
│   └── posts_analysis/               # Post analysis JSON files
│
├── docs/                              # Documentation
│   ├── QUICK_START.md                # Quick reference guide
│   └── TRENDING_DATA_GUIDE.md        # Detailed documentation
│
├── debug_screenshots/                 # Debug screenshots (if issues occur)
├── old_scripts/                       # Deprecated scripts
├── google_groups/                     # Separate Google Workspace project (ignore)
└── venv/                              # Python virtual environment
```

---

## 🚀 Quick Start

### 1. Setup (One-time)

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Verify setup
python scrapers/test_setup.py
```

### 2. Run the Pipeline

#### Option A: Run Once
```bash
python scrapers/trending_data_pipeline.py
```

#### Option B: Run on Schedule (Every 4 Hours)
```bash
python scrapers/trending_data_pipeline.py --schedule
```

#### Option C: Custom Schedule
```bash
python scrapers/trending_data_pipeline.py --schedule 3  # Every 3 hours
```

### 3. Get Your Results

**Find the final output here:**
```
outputs/pipeline_results/trending_data_pipeline_YYYYMMDD_HHMMSS.json
```

This JSON file contains everything your teammate needs for analysis! 🎉

---

## 📊 Output Files Explained

### 🎯 Main Output (What Your Teammate Needs)
**Location:** `outputs/pipeline_results/trending_data_pipeline_*.json`

**Contains:**
- All Google Trends data (trending searches, search volumes)
- All Twitter trending topics from 4 tabs
- Actual posts from X.com with engagement metrics
- Key insights summary
- Metadata and timestamps

### Individual Outputs

| File | Location | Description |
|------|----------|-------------|
| Google Trends CSV | `outputs/google_trends/` | Trending searches with search volume |
| Twitter Trends JSON | `outputs/twitter_trends/` | Trending topics from 4 Twitter tabs |
| Posts Analysis JSON | `outputs/posts_analysis/` | Extracted posts with engagement data |

---

## 🔑 Environment Variables

Required in `.env` file:
```env
BROWSERBASE_API_KEY=bb_live_...
BROWSERBASE_PROJECT_ID=...
```

> **Note:** Tavily API key is currently hardcoded in scripts. Update if needed.

---

## 🔧 Running Individual Scrapers

You can run each scraper independently for testing:

```bash
# Google Trends only
python scrapers/google_trends_browserbase_scraper.py

# Twitter Trends only
python scrapers/twitter_browserbase_scraper.py

# Post Analysis only (auto-finds latest files)
python scrapers/twitter_post_analyzer.py
```

---

## 📖 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Commands and quick reference
- **[Full Documentation](docs/TRENDING_DATA_GUIDE.md)** - Detailed guide with troubleshooting

---

## 🐛 Troubleshooting

### Setup Issues
```bash
# Run setup test
python scrapers/test_setup.py
```

### Scraping Issues
- Check `debug_screenshots/` for visual debugging
- Verify `.env` credentials
- See [TRENDING_DATA_GUIDE.md](docs/TRENDING_DATA_GUIDE.md) for common issues

### Twitter Login Requirements
Some regions may require Twitter login. If scraping fails:
1. Check screenshots in `debug_screenshots/`
2. Consider adjusting selectors in `twitter_browserbase_scraper.py`

---

## 📦 What Gets Installed

```
browserbase              # Browserless browser automation
playwright               # Browser automation
tavily-python            # Tavily search API
schedule                 # Task scheduling
python-dotenv            # Environment variables
requests                 # HTTP library
```

---

## 🔄 Scheduling Options

### Built-in Scheduler (Recommended)
```bash
python scrapers/trending_data_pipeline.py --schedule 4
```

### Cron (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add line (runs every 4 hours)
0 */4 * * * cd /path/to/project && source venv/bin/activate && python scrapers/trending_data_pipeline.py
```

### PM2 (Node.js)
```bash
pm2 start scrapers/trending_data_pipeline.py --interpreter python3 --name "trending-scraper"
```

---

## 📤 For Your Teammate

**Send them this file:**
```
outputs/pipeline_results/trending_data_pipeline_[latest].json
```

**It contains:**
- ✅ All trending topics from Google & Twitter
- ✅ Actual posts with content and engagement metrics
- ✅ Structured JSON ready for analysis
- ✅ Timestamps and metadata

---

## 🎯 System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   TRENDING DATA PIPELINE                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  STEP 1: Scrape Google Trends           │
        │  → trending_US_4h_YYYYMMDD-HHMM.csv     │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  STEP 2: Scrape Twitter Trending Tabs   │
        │  → twitter_trending_*.json               │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  STEP 3: Analyze Keywords & Get Posts   │
        │  → trending_posts_analysis_*.json        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  STEP 4: Generate Final Unified JSON    │
        │  → trending_data_pipeline_*.json ⭐      │
        └─────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Browserbase** - Cloud browser automation (no local Chrome needed)
- **Playwright** - Browser control
- **Tavily API** - Supplemental search data
- **Schedule** - Task scheduling

---

## 📝 Notes

- **Google Workspace Files**: The `google_groups/`, `credentials.json`, and `README_GOOGLE_GROUPS.md` are from a separate project and can be ignored for this trending data system.
- **Old Scripts**: Previous iterations are in `old_scripts/` for reference only.

---

## ✨ Features

✅ **No Twitter API needed** - Direct scraping via Browserbase
✅ **Hybrid approach** - Combines Browserbase + Tavily for maximum data
✅ **Auto-scheduling** - Set it and forget it
✅ **Error handling** - Saves debug screenshots when issues occur
✅ **Analyst-ready output** - Structured JSON with insights
✅ **Easy to run** - Single command execution

---

## 🤝 Support

1. Run `python scrapers/test_setup.py` to verify configuration
2. Check `debug_screenshots/` for visual debugging
3. Review error messages in console output
4. See [TRENDING_DATA_GUIDE.md](docs/TRENDING_DATA_GUIDE.md) for detailed troubleshooting

---

## 📄 License

Internal project for Storika team.

---

**Made with ❤️ for trending data analysis**
