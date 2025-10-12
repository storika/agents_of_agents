"""
HR Validation with Recent Posts
최근 post 데이터만으로 간편하게 HR validation 실행
"""

import asyncio
import json
from google.adk.runners import InMemoryRunner
from google.genai import types
from hr_validation_agent.agent import root_agent
from hr_validation_agent.tools_prompt_loader import create_hr_input_from_posts


async def run_hr_with_recent_posts(
    recent_posts: list,
    iteration: int = 1
):
    """
    Run HR validation with recent post performance data
    
    Args:
        recent_posts: List of recent post data with performance metrics
        iteration: Current iteration number
    
    Example post format:
        {
            "content_id": "post_123",
            "contributors": ["research", "creative_writer", "generator"],
            "internal_scores": {
                "clarity": 0.75,
                "novelty": 0.68,
                "shareability": 0.50,
                "credibility": 0.80,
                "safety": 0.95
            },
            "actual_performance": {
                "impressions": 5000,
                "likes": 120,
                "retweets": 25,
                "replies": 8,
                "engagement_rate": 0.031
            }
        }
    """
    print("=" * 80)
    print("🤖 HR Validation with Recent Posts")
    print("=" * 80)
    print()
    
    # Create HR input from posts
    print(f"📊 Processing {len(recent_posts)} recent posts...")
    hr_input_json = create_hr_input_from_posts(
        json.dumps(recent_posts, ensure_ascii=False),
        iteration=iteration
    )
    
    hr_input = json.loads(hr_input_json)
    
    if "error" in hr_input:
        print(f"❌ Error creating HR input: {hr_input['error']}")
        return
    
    print(f"✅ Created HR input for iteration {hr_input['iteration']}")
    print(f"   Layers: {len(hr_input['layers'])}")
    print()
    
    # Save HR input for reference
    output_file = f"hr_input_iteration_{iteration}_from_posts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(hr_input, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved HR input to: {output_file}")
    print()
    
    # Run HR validation agent
    print("🚀 Running HR Validation Agent (Sequential)...")
    print()
    
    runner = InMemoryRunner(agent=root_agent, app_name="hr_validation_agent")
    session_service = runner.session_service
    
    user_id = "user_01"
    session_id = f"session_iteration_{iteration}"
    
    await session_service.create_session(
        app_name="hr_validation_agent",
        user_id=user_id,
        session_id=session_id,
    )
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=json.dumps(hr_input, ensure_ascii=False))]
        ),
    ):
        if event.is_final_response() and event.content:
            final_text = event.content.parts[0].text.strip()
            print("\n" + "=" * 80)
            print("✅ HR Validation Complete!")
            print("=" * 80)
            print()
            print(final_text)
            
            # Save results
            result_file = f"hr_results_iteration_{iteration}_from_posts.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                f.write(final_text)
            print()
            print(f"💾 Results saved to: {result_file}")


def run_sync(recent_posts: list, iteration: int = 1):
    """Synchronous wrapper"""
    asyncio.run(run_hr_with_recent_posts(recent_posts, iteration))


# ===== EXAMPLE USAGE =====

if __name__ == "__main__":
    # Example: Recent posts with performance data
    sample_posts = [
        {
            "content_id": "post_001",
            "contributors": ["research", "creative_writer", "generator"],
            "internal_scores": {
                "clarity": 0.78,
                "novelty": 0.72,
                "shareability": 0.48,
                "credibility": 0.80,
                "safety": 0.95
            },
            "actual_performance": {
                "impressions": 5000,
                "likes": 120,
                "retweets": 18,
                "replies": 5,
                "engagement_rate": 0.029
            }
        },
        {
            "content_id": "post_002",
            "contributors": ["research", "creative_writer", "generator"],
            "internal_scores": {
                "clarity": 0.75,
                "novelty": 0.68,
                "shareability": 0.50,
                "credibility": 0.78,
                "safety": 0.92
            },
            "actual_performance": {
                "impressions": 3200,
                "likes": 85,
                "retweets": 12,
                "replies": 3,
                "engagement_rate": 0.031
            }
        },
        {
            "content_id": "post_003",
            "contributors": ["research", "creative_writer", "generator"],
            "internal_scores": {
                "clarity": 0.80,
                "novelty": 0.70,
                "shareability": 0.45,
                "credibility": 0.82,
                "safety": 0.90
            },
            "actual_performance": {
                "impressions": 2800,
                "likes": 70,
                "retweets": 8,
                "replies": 2,
                "engagement_rate": 0.029
            }
        }
    ]
    
    print("📝 Sample Data:")
    print(f"   {len(sample_posts)} recent posts")
    print(f"   Avg engagement rate: {sum(p['actual_performance']['engagement_rate'] for p in sample_posts) / len(sample_posts):.3f}")
    print()
    
    run_sync(sample_posts, iteration=1)

