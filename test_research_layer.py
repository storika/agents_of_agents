"""
Test script to verify research subagent correctly fetches and processes trend data
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from cmo_agent.sub_agents import load_latest_trend_data, call_research_layer
import json


def test_load_trend_data():
    """Test if we can load the latest trend data"""
    print("=" * 80)
    print("TEST 1: Loading Latest Trend Data")
    print("=" * 80)

    data = load_latest_trend_data()

    if data:
        print("✅ Successfully loaded trend data")
        print(f"   - Data sources: {data.get('metadata', {}).get('data_sources', [])}")
        print(f"   - Collection time: {data.get('metadata', {}).get('collection_timestamp', 'N/A')}")

        # Check structure
        twitter_data = data.get('twitter_trending', {})
        print(f"   - Twitter trends: {len(twitter_data.get('all_keywords', []))} keywords")

        post_analysis = data.get('post_analysis', {})
        print(f"   - Post analysis: {len(post_analysis.get('keywords', []))} keywords analyzed")
        print(f"   - Total posts: {post_analysis.get('total_posts_extracted', 0)}")

        return True
    else:
        print("❌ Failed to load trend data")
        return False


def test_research_layer_with_real_data():
    """Test if research layer correctly uses the loaded trend data"""
    print("\n" + "=" * 80)
    print("TEST 2: Research Layer Processing with Real Trend Data")
    print("=" * 80)

    # Call research layer (will load trend data internally)
    result = call_research_layer(
        topic=None,  # Let it discover from trend data
        audience_demographics="AI/ML developers, indie hackers, founders"
    )

    print("\n📊 Research Layer Results:")
    print(f"   - Trending topics found: {len(result.get('trending_topics', []))}")
    print(f"   - Data sources used: {result.get('data_sources_used', [])}")
    print(f"   - Collection timestamp: {result.get('collection_timestamp', 'N/A')}")
    print(f"   - Perturbations applied: {len(result.get('perturbations_applied', []))}")

    # Show first trending topic
    topics = result.get('trending_topics', [])
    if topics:
        print(f"\n   First Topic:")
        first_topic = topics[0]
        print(f"     - Name: {first_topic.get('topic_name', 'N/A')}")
        print(f"     - Source: {first_topic.get('source', 'N/A')}")
        print(f"     - Relevance: {first_topic.get('relevance_score', 0):.2f}")
        print(f"     - Timeliness: {first_topic.get('timeliness_score', 0):.2f}")

    # Check if it used real data or fallback
    data_sources = result.get('data_sources_used', [])
    used_real_data = any('Fallback' not in str(source) for source in data_sources)

    if used_real_data:
        print("\n✅ Research layer is using REAL trend data")
    else:
        print("\n⚠️  Research layer fell back to default data")

    # Show viral angles
    viral_angles = result.get('viral_potential_angles', [])
    print(f"\n   Viral Angles Generated: {len(viral_angles)}")
    if viral_angles:
        print(f"     First angle: {viral_angles[0].get('angle_summary', 'N/A')}")

    return used_real_data


def test_perturbation_quality():
    """Check if the research layer adds meaningful perturbations"""
    print("\n" + "=" * 80)
    print("TEST 3: Perturbation Quality Check")
    print("=" * 80)

    result = call_research_layer()

    perturbations = result.get('perturbations_applied', [])
    print(f"   - Perturbations applied: {len(perturbations)}")

    if perturbations:
        print("   - Details:")
        for i, p in enumerate(perturbations[:3], 1):
            print(f"     {i}. {p}")
        print("\n✅ Research layer is applying perturbations")
        return True
    else:
        print("⚠️  No perturbations found (might need to check agent prompt)")
        return False


if __name__ == "__main__":
    print("\n" + "🔬 Testing Research Subagent Integration with Trend Data " + "\n")

    test1_pass = test_load_trend_data()

    if test1_pass:
        test2_pass = test_research_layer_with_real_data()
        test3_pass = test_perturbation_quality()

        print("\n" + "=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        print(f"✅ Test 1 (Load Trend Data): {'PASS' if test1_pass else 'FAIL'}")
        print(f"✅ Test 2 (Use Real Data): {'PASS' if test2_pass else 'FAIL'}")
        print(f"✅ Test 3 (Apply Perturbations): {'PASS' if test3_pass else 'FAIL'}")

        if test1_pass and test2_pass and test3_pass:
            print("\n🎉 ALL TESTS PASSED! Research subagent is correctly fetching")
            print("   and processing trend data with perturbations.")
        else:
            print("\n⚠️  Some tests failed. Check details above.")
    else:
        print("\n❌ Cannot proceed with other tests without trend data.")
        print("   Run the pipeline first: python trend_research_pipeline/pipeline.py")
