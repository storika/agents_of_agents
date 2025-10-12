# 📁 Project Structure

Clean, organized structure for the Trending Data Collection System.

## 🎯 Main Directories

```
trending-data-collection/
│
├── 📖 README.md                    # Main documentation (START HERE!)
├── 📦 requirements.txt             # Python dependencies
├── 🔐 .env                         # Environment variables (API keys)
│
├── 📁 scrapers/                    # ⭐ Main scripts (run from here)
│   ├── trending_data_pipeline.py         # 🚀 MAIN - Run this!
│   ├── google_trends_browserbase_scraper.py
│   ├── twitter_browserbase_scraper.py
│   ├── twitter_post_analyzer.py
│   └── test_setup.py                     # Verify setup
│
├── 📁 outputs/                     # All generated data
│   ├── pipeline_results/                 # ⭐ Final unified JSONs
│   ├── google_trends/                    # Google Trends CSVs
│   ├── twitter_trends/                   # Twitter trending JSONs
│   └── posts_analysis/                   # Post analysis JSONs
│
├── 📁 docs/                        # Documentation
│   ├── QUICK_START.md                    # Quick reference
│   └── TRENDING_DATA_GUIDE.md            # Detailed guide
│
├── 📁 debug_screenshots/           # Debug images (auto-generated)
├── 📁 old_scripts/                 # Previous versions (ignore)
├── 📁 google_groups/               # Separate project (ignore)
└── 📁 venv/                        # Python virtual environment
```

---

## 🚀 How to Use

### Quick Start
```bash
cd scrapers/
source ../venv/bin/activate
python test_setup.py               # Verify everything is ready
python trending_data_pipeline.py   # Run the pipeline!
```

### Find Your Results
```bash
outputs/pipeline_results/trending_data_pipeline_YYYYMMDD_HHMMSS.json
```

---

## 📂 Directory Details

### `/scrapers/` - Main Scripts
All the executable Python scripts. Run commands from this directory.

| File | Purpose |
|------|---------|
| `trending_data_pipeline.py` | **Main orchestrator** - Runs all scrapers |
| `google_trends_browserbase_scraper.py` | Scrapes Google Trends |
| `twitter_browserbase_scraper.py` | Scrapes Twitter trending tabs |
| `twitter_post_analyzer.py` | Analyzes keywords & extracts posts |
| `test_setup.py` | Verifies system setup |

### `/outputs/` - Generated Data

| Folder | Contains |
|--------|----------|
| `pipeline_results/` | **⭐ Final unified JSONs** - Send these to your teammate! |
| `google_trends/` | Google Trends CSV files |
| `twitter_trends/` | Twitter trending JSON files |
| `posts_analysis/` | Post analysis JSON files |

### `/docs/` - Documentation

| File | Purpose |
|------|---------|
| `QUICK_START.md` | Quick reference commands |
| `TRENDING_DATA_GUIDE.md` | Detailed guide with troubleshooting |

### `/debug_screenshots/` - Debugging
Auto-generated screenshots when scrapers encounter issues. Check these if something fails.

### `/old_scripts/` - Archive
Previous versions and deprecated code. Safe to ignore.

### `/google_groups/` - Separate Project
Google Workspace group creation tool. Not related to trending data system.

---

## 🎯 Typical Workflow

```
1. Activate environment
   cd scrapers/
   source ../venv/bin/activate

2. Run pipeline
   python trending_data_pipeline.py

3. Get results
   Check: ../outputs/pipeline_results/trending_data_pipeline_[timestamp].json

4. Send to teammate
   That JSON file contains everything!
```

---

## 🔄 Automated Scheduling

```bash
cd scrapers/
python trending_data_pipeline.py --schedule    # Runs every 4 hours
```

Output files will accumulate in `/outputs/pipeline_results/` with timestamps.

---

## 📊 Output File Naming Convention

| Pattern | Example | Location |
|---------|---------|----------|
| `trending_US_4h_*.csv` | `trending_US_4h_20251011-1633.csv` | `outputs/google_trends/` |
| `twitter_trending_browserbase_*.json` | `twitter_trending_browserbase_20251011_160000.json` | `outputs/twitter_trends/` |
| `trending_posts_analysis_*.json` | `trending_posts_analysis_20251011_161000.json` | `outputs/posts_analysis/` |
| `trending_data_pipeline_*.json` | `trending_data_pipeline_20251011_162000.json` | `outputs/pipeline_results/` ⭐ |

---

## 🧹 Maintenance

### Clean Old Outputs (Optional)
```bash
# Keep only last 7 days of output files
cd outputs/pipeline_results/
ls -t | tail -n +8 | xargs rm
```

### Update Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## ✅ What Your Teammate Needs

**Just send them the latest file from:**
```
outputs/pipeline_results/trending_data_pipeline_[latest-timestamp].json
```

That's it! It contains everything in one structured JSON file.

---

**Made with ❤️ for clean, organized trending data collection**
