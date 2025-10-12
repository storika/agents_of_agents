# Quick Start Guide

## TL;DR

```bash
# 1. Start automated collection (runs every 3 hours)
cd trend_research_pipeline
python scheduler.py

# 2. Generate content (CMO auto-reads latest trends)
python -c "from cmo_agent.agent import root_agent; root_agent.execute('Generate content')"
```

## What This Does

### Automated Collection (Every 3 Hours)

```
trend_research_pipeline/scheduler.py
  ↓
[Scrape Google Trends] → CSV
[Scrape Twitter Trends] → JSON
[Analyze Posts] → JSON
  ↓
Save: trend_data/trending_20251011_183000.json
```

### CMO Content Generation (On-Demand)

```
cmo_agent/agent.py
  ↓
Research Layer (sub_agents.py)
  ↓
Load: trend_data/trending_20251011_183000.json (latest)
  ↓
Apply perturbation & creative analysis
  ↓
Feed to Creative Writer → Generator → Critic → Safety → Selector
  ↓
Output: {text, media_prompt, image, scores}
```

## Commands

### Collection

```bash
# Run once
python pipeline.py

# Run every 3 hours (automated)
python scheduler.py

# Run every 2 hours (custom interval)
python scheduler.py --interval 2

# Run once with scheduler logging
python scheduler.py --once
```

### Verification

```bash
# Check trend data files
ls -lh ../trend_data/

# View latest file
tail -100 ../trend_data/trending_*.json | tail -1

# Count collections
ls -1 ../trend_data/trending_*.json | wc -l
```

## Integration Test

```python
# Test trend data loading
from cmo_agent.sub_agents import load_latest_trend_data

data = load_latest_trend_data()
if data:
    print("✅ Trend data loaded successfully")
    print(f"Collected at: {data['pipeline_metadata']['pipeline_timestamp']}")
else:
    print("⚠️ No trend data found - run pipeline first")

# Test full research layer
from cmo_agent.sub_agents import call_research_layer

result = call_research_layer()
print(f"Found {len(result['trending_topics'])} trending topics")
```

## Expected Output Structure

### trend_data/trending_*.json (Raw Collection)

```json
{
  "pipeline_metadata": {...},
  "data_sources": {
    "google_trends": {"data": [...]},
    "twitter_trends": {"data": {...}},
    "trending_posts": {"data": {...}}
  },
  "key_insights": {...}
}
```

### Research Layer Output (After Analysis)

```json
{
  "trending_topics": [
    {
      "topic_name": "Multi-Agent Systems",
      "relevance_score": 0.96,
      "timeliness_score": 0.99,
      "hashtags": ["#AIAgents", "#BuildInPublic"]
    }
  ],
  "viral_potential_angles": [
    {
      "angle_summary": "Behind-the-scenes debugging",
      "hook_template": "We debugged 1000 agent failures...",
      "why_viral": "Transparency + real data"
    }
  ],
  "perturbations_applied": ["Added contrarian take"]
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No trend data | Run `python pipeline.py` once |
| Scraper fails | Check Browserbase credentials in `.env` |
| CMO doesn't read data | Verify `trend_data/*.json` exists |
| Old data | Check scheduler is running: `ps aux \| grep scheduler` |

## Configuration

Edit `config.py`:

```python
COLLECTION_INTERVAL_HOURS = 3  # Change interval
MAX_GOOGLE_TRENDS = 25         # Items to collect
MAX_KEYWORDS_TO_ANALYZE = 10   # Keywords to analyze
```

## Production Deployment

Use cron instead of Python scheduler:

```bash
# Edit crontab
crontab -e

# Add entry (every 3 hours)
0 */3 * * * cd /path/to/trend_research_pipeline && python pipeline.py >> /var/log/trend.log 2>&1
```

## Next Steps

1. Start scheduler: `python scheduler.py`
2. Wait for first collection (check `trend_data/`)
3. Test CMO integration: `call_research_layer()`
4. Generate content: CMO agent automatically uses latest trends

See `README.md` for detailed documentation.
