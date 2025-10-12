#!/usr/bin/env python3
"""
Test trend data integration between pipeline and CMO agent.
Creates a mock trend data file and verifies CMO can read it.
"""

import json
from datetime import datetime
from pathlib import Path

# Create mock trend data
mock_data = {
    "pipeline_metadata": {
        "pipeline_timestamp": datetime.now().isoformat(),
        "pipeline_version": "1.0",
        "pipeline_description": "Mock trend data for testing",
        "collection_interval_hours": 3
    },
    "data_sources": {
        "google_trends": {
            "collected": True,
            "trends_count": 3,
            "data": [
                {"Trends": "AI Agents", "Search volume": "500K+"},
                {"Trends": "Multi-Agent Systems", "Search volume": "200K+"},
                {"Trends": "LangChain", "Search volume": "150K+"}
            ]
        },
        "twitter_trends": {
            "collected": True,
            "data": {
                "tabs": {
                    "For you": {
                        "success": True,
                        "trending_topics": [
                            {"topic_name": "#AIAgents", "post_count": "50K posts"},
                            {"topic_name": "#BuildInPublic", "post_count": "30K posts"}
                        ]
                    }
                }
            }
        },
        "trending_posts": {
            "collected": True,
            "data": {
                "summary": {
                    "total_posts_extracted": 150,
                    "total_keywords_analyzed": 10
                }
            }
        }
    },
    "key_insights": {
        "top_google_trends": [
            {"keyword": "AI Agents", "search_volume": "500K+"},
            {"keyword": "Multi-Agent Systems", "search_volume": "200K+"}
        ],
        "top_twitter_trends": [
            {"keyword": "#AIAgents", "tab": "For you", "post_count": "50K posts"}
        ],
        "total_posts_analyzed": 150
    }
}

# Save to trend_data/
trend_data_dir = Path(__file__).parent / "trend_data"
trend_data_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"trending_{timestamp}.json"
filepath = trend_data_dir / filename

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(mock_data, f, indent=2, ensure_ascii=False)

print(f"✅ Created mock trend data: {filepath}")
print(f"   Location: {filepath.relative_to(Path.cwd())}")
print()

# Test CMO integration
print("🔍 Testing CMO agent integration...")
try:
    from cmo_agent.sub_agents import load_latest_trend_data

    data = load_latest_trend_data()

    if data:
        print("✅ CMO agent successfully loaded trend data!")
        print(f"   Pipeline timestamp: {data['pipeline_metadata']['pipeline_timestamp']}")
        print(f"   Google trends count: {data['data_sources']['google_trends']['trends_count']}")
        print(f"   Total posts analyzed: {data['key_insights']['total_posts_analyzed']}")
        print()
        print("🎉 Integration working perfectly!")
        print()
        print("Next steps:")
        print("  1. Run real pipeline: uv run python trend_research_pipeline/pipeline.py")
        print("  2. CMO will automatically read the latest trending_*.json file")
        print("  3. Generate content: from cmo_agent.agent import root_agent")
    else:
        print("❌ Failed to load trend data")

except Exception as e:
    print(f"❌ Error testing integration: {e}")
    import traceback
    traceback.print_exc()
