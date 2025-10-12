"""
CMO Agent를 이전 컨텐츠 히스토리와 트렌드 데이터와 함께 실행하는 예제
"""

import json
from use_content_history import load_content_history, format_context_for_research


def run_cmo_with_history():
    """
    히스토리 데이터를 포함하여 CMO Agent 실행
    """
    
    print("="*70)
    print("🚀 CMO Agent with Content History & Trends")
    print("="*70)
    
    # 1. 히스토리 데이터 로드
    print("\n📊 Loading content history...")
    history = load_content_history("content_history_sample.json")
    context = format_context_for_research(history)
    
    print(f"✓ Loaded {len(history.get('content_history', []))} historical posts")
    print(f"✓ Current trends date: {history.get('current_trends', {}).get('date')}")
    
    # 2. 주제 및 청중 설정
    topic = "AI agents that hire other AI agents for WeaveHacks2"
    audience = "AI/ML Engineers, Tech Founders, Developer Community"
    
    print(f"\n🎯 Topic: {topic}")
    print(f"👥 Audience: {audience}")
    
    # 3. Enhanced prompt with historical context
    enhanced_prompt = f"""
{context}

=== NEW CONTENT REQUEST ===

Topic: {topic}
Target Audience: {audience}

Based on the historical performance data above:
1. Identify what content types worked best (behind-the-scenes had 9.2% engagement)
2. Apply the tone that resonated (humorous + transparent performed best)
3. Consider current trending topics (AI Agents trend score: 0.92)
4. Follow the recommendations (short 80-120 chars, avoid over-promotion)

Generate content that builds on our best-performing patterns while staying fresh and relevant to current trends.
"""
    
    print("\n" + "="*70)
    print("📝 Enhanced Prompt for CMO Agent:")
    print("="*70)
    print(enhanced_prompt[:300] + "...\n[truncated for display]")
    
    # 4. ADK를 사용하여 실제 실행하는 방법
    print("\n" + "="*70)
    print("🤖 To Run with ADK:")
    print("="*70)
    
    run_instructions = """
# Option 1: Using ADK Tools
adk run cmo_agent --input "AI agents that hire other AI agents"

# Option 2: Using Python API
from google.adk.runners import InMemoryRunner
from cmo_agent.agent import root_agent

runner = InMemoryRunner(root_agent, "cmo_agent")
session = runner.session_service().create_session("cmo_agent", "user_01").blockingGet()

# Enhanced message with context
message = Content.fromParts(Part.fromText(enhanced_prompt))
events = runner.runAsync("user_01", session.id(), message)

# Process results
for event in events.blockingIterable():
    if event.finalResponse():
        print(event.stringifyContent())
"""
    
    print(run_instructions)
    
    # 5. Expected workflow
    print("\n" + "="*70)
    print("📋 Expected Workflow:")
    print("="*70)
    print("""
1. Research Agent receives historical context + current trends
   → Analyzes what worked (behind-the-scenes, humor, transparency)
   → Identifies current trending topics (AI Agents: 0.92, Weave: 0.78)
   → Recommends angles based on data

2. LoopAgent generates 10 content variations
   → Creative Writer: 10 different ideas (applying lessons learned)
   → Generator: Creates actual content for each idea
   → Critic: Evaluates each variation
   
3. System selects best result
   → Ranks all 10 by overall score
   → Applies weights based on historical performance
   → Selects highest-scoring content

4. Safety Agent validates
   → Final safety and compliance check
   → Returns approved/rejected/needs_improvement

5. Result includes:
   ✓ Best content from 10 iterations
   ✓ All iteration scores for comparison
   ✓ Performance predictions based on historical patterns
""")
    
    # 6. Sample expected output structure
    print("\n" + "="*70)
    print("📤 Expected Output Structure:")
    print("="*70)
    
    sample_output = {
        "status": "approved",
        "total_iterations": 10,
        "best_iteration": 7,
        "best_content": {
            "idea": {
                "title": "Behind the Scenes: When AI Rejects AI",
                "hook": "Our CMO Agent just rejected content from our Writer Agent. Awkward.",
                "angle": "Transparent look at multi-agent quality control",
                "novelty_score": 0.85,
                "creativity_score": 0.88,
                "engagement_potential_score": 0.92
            },
            "generator_output": {
                "content_pieces": [
                    {
                        "platform": "Twitter",
                        "content": "Plot twist: Our CMO Agent (powered by LoopAgent) rejected content from Writer Agent in iteration 3. \n\nQuality control is ruthless when AIs manage AIs. 😅\n\n#BuildInPublic #AIAgents",
                        "character_count": 118,
                        "clarity_score": 0.88,
                        "shareability_score": 0.90
                    }
                ]
            },
            "predicted_performance": {
                "engagement_rate": 0.089,
                "reasoning": "Similar to post_004 (highest performer): humor + transparency + behind-the-scenes"
            }
        },
        "final_scores": {
            "overall": 0.88,
            "novelty": 0.85,
            "creativity": 0.88,
            "engagement": 0.92,
            "clarity": 0.88,
            "shareability": 0.90,
            "quality": 0.85,
            "safety": 0.95
        },
        "all_iteration_scores": [
            {"iteration": 1, "overall_score": 0.72, "idea_title": "Data-Driven Content Creation"},
            {"iteration": 2, "overall_score": 0.75, "idea_title": "Multi-Agent Team Dynamics"},
            {"iteration": 7, "overall_score": 0.88, "idea_title": "Behind the Scenes: When AI Rejects AI"},
            "... 7 more iterations ..."
        ],
        "why_this_won": [
            "Builds on best-performing pattern (behind-the-scenes like post_004)",
            "Uses successful tone (humorous + transparent)",
            "Optimal length (118 chars vs recommended 80-120)",
            "Leverages current trend (AI Agents: 0.92 trend score)",
            "Authentic BuildInPublic moment"
        ]
    }
    
    print(json.dumps(sample_output, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("✨ Ready to run CMO Agent with historical context!")
    print("="*70)


if __name__ == "__main__":
    run_cmo_with_history()

