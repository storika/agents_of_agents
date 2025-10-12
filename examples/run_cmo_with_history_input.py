"""
CMO Agent에 컨텐츠 히스토리와 트렌드 데이터를 입력으로 제공하는 예제
"""

import json


def create_content_request_with_history():
    """
    히스토리 데이터를 포함한 컨텐츠 요청 생성
    """
    
    # 1. 히스토리 데이터 로드 (실제로는 DB나 파일에서 가져옴)
    with open("examples/content_history_sample.json", "r", encoding="utf-8") as f:
        history_data = json.load(f)
    
    # 2. CMO Agent에 제공할 입력 메시지 생성
    request_message = f"""
Generate next content for Twitter/X.

Here is our historical performance data and current trends:

{json.dumps(history_data, indent=2, ensure_ascii=False)}

Based on this data:
- Our best performing content had 9.2% engagement (behind-the-scenes, humorous tone)
- Current trending topics: AI Agents (0.92), Build in Public (0.85)
- Audience: AI/ML Engineers, Tech Founders, Developers
- Recommendations: Use humor when authentic, keep it 80-120 chars, show transparency

Please generate the next high-performing content piece.
"""
    
    return request_message


def create_simple_request_without_history():
    """
    히스토리 없이 간단하게 요청
    """
    return "Give me next content"


def main():
    """메인 실행 예제"""
    
    print("="*70)
    print("CMO Agent Input Examples")
    print("="*70)
    
    # 예제 1: 히스토리 데이터 포함
    print("\n📊 Example 1: With Historical Data")
    print("="*70)
    request_with_history = create_content_request_with_history()
    print(request_with_history[:500] + "...\n[truncated for display]")
    
    # 예제 2: 히스토리 없음
    print("\n📝 Example 2: Without Historical Data")
    print("="*70)
    request_simple = create_simple_request_without_history()
    print(request_simple)
    
    # ADK 실행 방법
    print("\n" + "="*70)
    print("🚀 How to Run with ADK")
    print("="*70)
    
    print("""
# Option 1: Using ADK CLI with history file
adk run cmo_agent --input "$(cat examples/content_history_sample.json | jq -c) Generate next content"

# Option 2: Using Python API
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from cmo_agent.agent import root_agent

# Create runner
runner = InMemoryRunner(root_agent, "cmo_agent")
session = runner.session_service().create_session("cmo_agent", "user_01").blockingGet()

# With history data
import json
with open("examples/content_history_sample.json") as f:
    history = json.load(f)

message_text = f'''
Generate next content.

Historical data:
{json.dumps(history, indent=2)}
'''

message = Content.fromParts(Part.fromText(message_text))
events = runner.runAsync("user_01", session.id(), message)

# Process results
for event in events.blockingIterable():
    if event.finalResponse():
        result = event.stringifyContent()
        print(result)
        
        # Parse and use the result
        content_result = json.loads(result)
        print(f"Selected: {content_result['selected']['text']}")
        print(f"Expected Score: {content_result['selected']['expected_overall']}")

# Option 3: Simple request without history
message_simple = Content.fromParts(Part.fromText("Give me next content"))
events = runner.runAsync("user_01", session.id(), message_simple)
""")
    
    # 예상 워크플로우
    print("\n" + "="*70)
    print("📋 Expected Workflow (With History)")
    print("="*70)
    print("""
1. CMO Agent receives request with historical data

2. Delegates to ContentPipeline:
   
   a. Research Agent:
      - Analyzes historical performance (best: behind-the-scenes, 9.2%)
      - Reviews current trends (AI Agents: 0.92)
      - Reads recommendations (humor, 80-120 chars, transparency)
      - Selects trending topic that aligns with successful patterns
   
   b. LoopAgent (10 iterations):
      - Creative Writer: Generates ideas following successful patterns
        → More behind-the-scenes content
        → Humorous + transparent tone
        → Developer-focused angles
      
      - Generator: Creates content with optimal format
        → 80-120 characters
        → Appropriate hashtags from trends
        → Clear media prompts
      
      - Critic: Evaluates quality
        → Compares to historical benchmarks
        → Scores against criteria
   
   c. Safety Agent: Final validation

3. CMO Agent:
   - Reviews all 10 iterations
   - Selects best based on overall score
   - Predicts performance based on historical similarity
   - Returns JSON with selected content

4. Output includes:
   ✓ All candidates with scores
   ✓ Best selected content
   ✓ Performance prediction
   ✓ Reasoning based on historical data
""")
    
    # 실제 사용 팁
    print("\n" + "="*70)
    print("💡 Usage Tips")
    print("="*70)
    print("""
1. Update history after each post:
   - Add actual performance metrics
   - Include feedback on what worked
   - Update trend data weekly

2. Structured vs Unstructured input:
   - Structured (recommended): Provide complete JSON with all fields
   - Unstructured: Just mention key insights in natural language
   - Both work! CMO Agent will parse accordingly

3. Continuous improvement:
   - More history = better predictions
   - Track which content types perform best
   - Let the agent learn from patterns

4. Override when needed:
   - Specific topic: "Generate content about [topic]"
   - Specific tone: "Make it more professional/funny/technical"
   - Agent will adapt while using historical insights
""")
    
    print("\n" + "="*70)
    print("✨ Ready to generate content with historical learning!")
    print("="*70)


if __name__ == "__main__":
    main()

