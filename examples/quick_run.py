"""
CMO Agent 빠른 실행 예제 - content_history + current_trends만 사용
"""

import json


def main():
    print("="*70)
    print("🚀 CMO Agent Quick Run Example")
    print("="*70)
    
    # 간단한 입력 로드
    with open("examples/simple_input.json", "r", encoding="utf-8") as f:
        input_data = json.load(f)
    
    print("\n📊 Input Data Summary:")
    print(f"  - Content History: {len(input_data['content_history'])} posts")
    print(f"  - Best Performer: post_004 (9.2% engagement)")
    print(f"  - Current Trends: {len(input_data['current_trends']['platform_trends']['twitter'])} topics")
    print(f"  - Top Trend: AI Agents (0.92 score)")
    
    # CMO Agent에 보낼 메시지
    message = f"""
Generate next content.

{json.dumps(input_data, indent=2, ensure_ascii=False)}
"""
    
    print("\n" + "="*70)
    print("📝 Message to CMO Agent:")
    print("="*70)
    print(message[:300] + "...\n")
    
    print("="*70)
    print("🤖 What CMO Agent Will Do:")
    print("="*70)
    print("""
1. Research Agent analyzes input:
   ✓ Identifies post_004 as best (humor + transparency)
   ✓ Finds pattern: behind-the-scenes content works (9.2%)
   ✓ Notes trending: AI Agents (0.92), Build in Public (0.85)
   ✓ Extracts successful hashtags: #AIAgents, #BuildInPublic

2. LoopAgent generates 10 variations:
   ✓ Creative Writer: Ideas following successful patterns
   ✓ Generator: Content with optimal format (80-120 chars)
   ✓ Critic: Evaluates each variation

3. Selects best from 10 iterations

4. Safety validation

5. Returns JSON with selected content + scores
""")
    
    print("="*70)
    print("💻 To Run with ADK:")
    print("="*70)
    print("""
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from cmo_agent.agent import root_agent
import json

# Load input
with open("examples/simple_input.json") as f:
    input_data = json.load(f)

# Create runner
runner = InMemoryRunner(root_agent, "cmo_agent")
session = runner.session_service().create_session("cmo_agent", "user_01").blockingGet()

# Send request
message_text = f'''
Generate next content.

{json.dumps(input_data, indent=2)}
'''

message = Content.fromParts(Part.fromText(message_text))
events = runner.runAsync("user_01", session.id(), message)

# Get result
for event in events.blockingIterable():
    if event.finalResponse():
        result = json.loads(event.stringifyContent())
        
        print("✨ Selected Content:")
        print(f"  Text: {result['selected']['text']}")
        print(f"  Score: {result['selected']['expected_overall']:.2f}")
        print(f"  Status: {result['publish_status']}")
""")
    
    print("\n" + "="*70)
    print("📋 Expected Output Format:")
    print("="*70)
    
    expected = {
        "candidates": [
            {
                "text": "Example tweet text...",
                "media_prompt": "...",
                "mode": "image",
                "scores": {
                    "clarity": 0.88,
                    "novelty": 0.85,
                    "shareability": 0.90,
                    "overall": 0.87
                }
            }
        ],
        "selected": {
            "text": "Behind the scenes: Our LoopAgent generated 47 tweets yesterday. Kept 1. That's a 2.1% success rate. And it's still better than our human CMO's 0% yesterday. 😅 #BuildInPublic",
            "media_prompt": "Humorous chart showing AI vs human content generation success rates",
            "mode": "image",
            "expected_overall": 0.89
        },
        "publish_status": "queued",
        "feedback_summary": "Following post_004 pattern: humor + transparency + behind-the-scenes. Trending topic alignment: AI Agents (0.92)."
    }
    
    print(json.dumps(expected, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("✅ Ready to generate content!")
    print("="*70)


if __name__ == "__main__":
    main()

