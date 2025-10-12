# Trend Research Pipeline

Clean pipeline for collecting trending data from X (Twitter) and Google Trends.

## Overview

The Trend Research Pipeline automatically scrapes and analyzes trending topics from multiple sources:
- **Google Trends**: Top trending searches with search volumes (via Browserbase + Gemini Vision OCR)
- **Twitter/X**: Trending topics from various categories (via Tavily API)
- **Post Analysis**: Actual posts related to trending keywords (via Tavily API)

Results are saved to `trend_data/` directory as timestamped JSON files, which are then consumed by the CMO agent's research layer.

## Architecture

```
trend_research_pipeline/
├── scrapers/
│   ├── google_trends_gemini.py    # Google Trends scraper (Browserbase + Gemini OCR)
│   ├── twitter_trends_tavily.py   # Twitter scraper (Tavily API)
│   └── post_analyzer.py           # Post content analyzer (Tavily API)
├── pipeline.py                    # Main orchestrator
├── scheduler.py                   # 3-hour scheduler
├── config.py                      # Configuration
└── requirements.txt

trend_data/                        # Output directory
└── trending_YYYYMMDD_HHMMSS.json
```

## Data Flow

```
[Every 3 hours - Automated]
trend_research_pipeline/
  1. Scrape Google Trends → CSV
  2. Scrape Twitter trending tabs → JSON
  3. Analyze posts from keywords
  4. Save unified JSON → trend_data/trending_YYYYMMDD_HHMMSS.json

[When CMO generates content - On-demand]
cmo_agent/sub_agents.py
  1. Read MOST RECENT trend_data/trending_*.json
  2. Apply perturbation & creative analysis
  3. Extract relevant topics for AI/ML audience
  4. Format for content generation pipeline
  5. Feed into Creative Writer layer
```

## Setup

### 1. Install Dependencies

```bash
cd trend_research_pipeline
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in project root:

```env
# Required for Google Trends OCR (via Gemini Vision)
GOOGLE_API_KEY=your_google_api_key
BROWSERBASE_API_KEY=your_browserbase_key
BROWSERBASE_PROJECT_ID=your_project_id

# Required for Twitter trends and post analysis
TAVILY_API_KEY=your_tavily_key
```

**Getting API Keys**:
- **Google API Key**: Get from [Google AI Studio](https://aistudio.google.com/apikey) (free tier available)
- **Browserbase**: For remote browser sessions (Google Trends screenshots)
- **Tavily**: For Twitter trends discovery (no login required)

**Note**: Twitter login credentials are no longer required. The pipeline uses Tavily API to discover trending topics from Twitter/X without requiring browser automation or authentication.

### 3. Verify Setup

```bash
python pipeline.py --help
```

## Usage

### Run Pipeline Once

Collect trend data once and exit:

```bash
python pipeline.py
```

Output: `trend_data/trending_YYYYMMDD_HHMMSS.json`

### Run on Schedule (Every 3 Hours)

Run pipeline continuously with 3-hour intervals:

```bash
python scheduler.py
```

### Custom Schedule Interval

Run with custom interval (e.g., every 2 hours):

```bash
python scheduler.py --interval 2
```

### Run Once via Scheduler

Use scheduler logging but run only once:

```bash
python scheduler.py --once
```

## Output Format

Each `trending_YYYYMMDD_HHMMSS.json` file contains:

```json
{
  "pipeline_metadata": {
    "pipeline_timestamp": "2025-10-11T18:30:00Z",
    "pipeline_version": "1.0",
    "collection_interval_hours": 3
  },
  "data_sources": {
    "google_trends": {
      "collected": true,
      "trends_count": 25,
      "data": [
        {
          "Trends": "Multi-Agent Systems",
          "Search volume": "500K+"
        }
      ]
    },
    "twitter_trends": {
      "collected": true,
      "data": {
        "tabs": {
          "For you": {
            "success": true,
            "trending_topics": [...]
          }
        }
      }
    },
    "trending_posts": {
      "collected": true,
      "data": {
        "keywords": [...],
        "summary": {...}
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

## Integration with CMO Agent

The CMO agent's research layer automatically:

1. **Loads** the most recent `trend_data/trending_*.json` file
2. **Analyzes** trending topics for relevance to AI/ML developer audience
3. **Enriches** with creative perturbation and viral angles
4. **Formats** for content generation pipeline

See: `cmo_agent/sub_agents.py::call_research_layer()`

## Scheduling with Cron (Production)

For production deployment, use cron instead of the Python scheduler:

```bash
# Edit crontab
crontab -e

# Add entry to run every 3 hours
0 */3 * * * cd /path/to/agents_of_agents/trend_research_pipeline && /path/to/python pipeline.py >> /path/to/logs/trend_pipeline.log 2>&1
```

## Troubleshooting

### No trend data collected

Check:
- Browserbase credentials in `.env`
- Twitter login credentials
- Network connectivity
- Browserbase session limits

### Pipeline fails at specific step

Each step is independent:
- If Google Trends fails, Twitter and post analysis continue
- If Twitter fails, Google Trends and post analysis continue
- Check error messages in console output

### CMO agent not reading trend data

Verify:
- `trend_data/` directory exists
- At least one `trending_*.json` file exists
- File is readable and valid JSON
- Check logs: "📊 Loading trend data from: trending_*.json"

## Configuration

Edit `config.py` to customize:

```python
# Collection interval (hours)
COLLECTION_INTERVAL_HOURS = 3

# Maximum items to collect
MAX_GOOGLE_TRENDS = 25
MAX_TWITTER_TRENDS_PER_TAB = 30
MAX_KEYWORDS_TO_ANALYZE = 10
MAX_POSTS_PER_KEYWORD = 10
```

## File Retention

Trend data files accumulate over time. Consider:

1. **Manual cleanup**: Remove old files periodically
2. **Automated cleanup**: Add cron job to delete files older than 7 days

```bash
# Delete files older than 7 days
find /path/to/trend_data -name "trending_*.json" -mtime +7 -delete
```

## Monitoring

Check pipeline health:

```bash
# Count trend data files
ls -1 trend_data/trending_*.json | wc -l

# View latest collection
ls -lt trend_data/trending_*.json | head -1

# Check file size (should be > 10KB)
du -h trend_data/trending_*.json | tail -1
```

## Development

### Add New Data Source

1. Create scraper in `scrapers/new_scraper.py`
2. Add step to `pipeline.py::TrendingDataPipeline`
3. Update `data_sources` in output JSON
4. Test with `python pipeline.py`

### Modify Output Schema

Edit `pipeline.py::_step_generate_final_output()` to change JSON structure.

**Note**: If schema changes, update CMO research agent prompt to match.

## Related Documentation

- Original scrapers: `trending-data-collection/` (legacy, kept for reference)
- CMO agent integration: `cmo_agent/sub_agents.py`
- Trend schema example: `trends_refactored.json`
