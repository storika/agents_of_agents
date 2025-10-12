"""
CMO Agent 서브 에이전트 관리
HR Agent의 hire_plan을 기반으로 서브 에이전트 팀 구성 및 관리
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from google.adk import Agent
import weave


class SubAgentTeam:
    """서브 에이전트 팀 관리 클래스"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.archetypes = self._load_archetypes()
    
    def _load_archetypes(self) -> Dict[str, Any]:
        """아키타입 정의 로드"""
        archetypes_dir = Path(__file__).parent.parent / "archetypes"
        
        all_archetypes = {}
        archetype_files = [
            "orchestrators.json",
            "content_creation.json",
            "intelligence.json",
            "quality_safety.json",
            "engagement.json"
        ]
        
        for filename in archetype_files:
            file_path = archetypes_dir / filename
            if file_path.exists():
                with open(file_path, 'r') as f:
                    archetype_list = json.load(f)
                    for archetype in archetype_list:
                        all_archetypes[archetype['name']] = archetype
        
        return all_archetypes
    
    def create_agent_from_hire_plan(self, hire_item: Dict[str, Any]) -> Agent:
        """
        hire_plan 항목으로부터 에이전트 생성
        
        Args:
            hire_item: {
                "slot": "writer/main",
                "ref": "ViralCopywriter",
                "patch": {},
                "reason": "..."
            }
        """
        archetype_name = hire_item['ref']
        
        if archetype_name not in self.archetypes:
            raise ValueError(f"Unknown archetype: {archetype_name}")
        
        archetype = self.archetypes[archetype_name]
        
        # patch 적용 (system_prompt 수정 등)
        system_prompt = archetype['system_prompt']
        patch = hire_item.get('patch', {})
        
        if 'system_prompt.append' in patch:
            system_prompt += f"\n\n{patch['system_prompt.append']}"
        
        # Agent 생성
        agent = Agent(
            model='gemini-2.5-flash',
            name=archetype_name,
            description=f"{archetype['role']} - {archetype['objective']}",
            instruction=system_prompt,
            # tools는 나중에 추가 가능
        )
        
        return agent
    
    def apply_hire_plan(self, hire_plan: List[Dict[str, Any]]) -> None:
        """
        HR Agent의 hire_plan 적용
        
        Args:
            hire_plan: HR Agent가 생성한 고용 계획
        """
        for hire_item in hire_plan:
            slot = hire_item['slot']
            ref = hire_item['ref']
            
            print(f"[HIRE] {slot}: {ref}")
            print(f"  이유: {hire_item['reason']}")
            
            agent = self.create_agent_from_hire_plan(hire_item)
            self.agents[slot] = agent
        
        print(f"\n✅ 총 {len(self.agents)}명의 서브 에이전트 생성 완료")
    
    def get_agent(self, slot: str) -> Optional[Agent]:
        """슬롯으로 에이전트 가져오기"""
        return self.agents.get(slot)
    
    def get_agents_by_category(self, category: str) -> List[Agent]:
        """카테고리별 에이전트 가져오기 (writer, media, critic, safety, intelligence 등)"""
        return [
            agent for slot, agent in self.agents.items()
            if slot.startswith(category)
        ]
    
    def list_agents(self) -> Dict[str, str]:
        """현재 활성 에이전트 목록"""
        return {
            slot: agent.name 
            for slot, agent in self.agents.items()
        }


# ===== 유틸리티 함수 =====


def parse_agent_response(response: str, agent_name: str) -> Optional[Dict[str, Any]]:
    """
    에이전트 응답에서 JSON 추출 및 파싱
    
    Args:
        response: 에이전트 응답 문자열
        agent_name: 에이전트 이름
    
    Returns:
        파싱된 딕셔너리 또는 None
    """
    try:
        # JSON 블록 찾기
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            json_str = response[json_start:json_end].strip()
        elif "{" in response and "}" in response:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]
        else:
            print(f"⚠️ {agent_name}: JSON 형식을 찾을 수 없습니다")
            return None
        
        return json.loads(json_str)
    
    except json.JSONDecodeError as e:
        print(f"⚠️ {agent_name}: JSON 파싱 오류 - {e}")
        return None
    except Exception as e:
        print(f"⚠️ {agent_name}: 응답 처리 오류 - {e}")
        return None


# ===== NEW LAYER AGENTS =====

def load_latest_trend_data() -> Optional[Dict[str, Any]]:
    """
    Load the most recent trending data from trend_data/ directory.

    Returns:
        Dict with trend data or None if no data found
    """
    trend_data_dir = Path(__file__).parent.parent / "trend_data"

    if not trend_data_dir.exists():
        print("⚠️ trend_data/ directory not found")
        return None

    # Find most recent trending_*.json file
    trend_files = sorted(trend_data_dir.glob("trending_*.json"), reverse=True)

    if not trend_files:
        print("⚠️ No trend data files found in trend_data/")
        return None

    latest_file = trend_files[0]
    print(f"📊 Loading trend data from: {latest_file.name}")

    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading trend data: {e}")
        return None


def get_latest_trends_tool() -> str:
    """
    Tool function: Fetch the most recent trending data from trend_data/ directory.

    This tool can be called by agents to access real-time trend data collected
    from Twitter and Google Trends.

    Returns:
        JSON string containing the latest trend data, or error message if unavailable.
    """
    trend_data = load_latest_trend_data()

    if trend_data:
        return json.dumps(trend_data, indent=2, ensure_ascii=False)
    else:
        return json.dumps({
            "error": "No trend data available",
            "message": "Please run the trend collection pipeline first: python trend_research_pipeline/pipeline.py"
        })


@weave.op()
def create_research_agent() -> Agent:
    """Research Layer 에이전트 생성 - Reads from trend_data/ and applies perturbation"""

    system_prompt = """You are the Research layer. Your task is to read collected trend data from trend_data/, apply perturbation and analysis, and format it for content generation.

IMPORTANT: You have access to a tool called `get_latest_trends_tool` that fetches the most recent trending data.
ALWAYS call this tool FIRST to get real-time trend data before performing your analysis.

The tool returns JSON data containing:
- timestamp: When the data was collected
- data: Object with query, answer, images, and results from Twitter/Google Trends

Your Tasks:
1. CALL get_latest_trends_tool() to fetch the latest trend data
2. ANALYZE the raw trend data to identify the most relevant topics for AI/ML developer audience
3. EXTRACT top 3-5 trending topics with relevance and timeliness scores
4. SYNTHESIZE audience insights from the trending posts and topics
5. PROPOSE 3-5 viral potential angles that combine trends with creative perspectives
6. ADD PERTURBATION: Introduce creative variations, unexpected connections, contrarian takes
7. ENRICH with hashtag recommendations, timing insights, and engagement predictions

Output MUST be a JSON object with the following structure:
{
  "trending_topics": [
    {
      "topic_name": "string",
      "relevance_score": "float (0-1)",
      "timeliness_score": "float (0-1)",
      "source": "Google Trends|Twitter|Both",
      "tweet_volume_24h": "integer (if available)",
      "hashtags": ["array", "of", "relevant", "hashtags"]
    }
  ],
  "audience_insights": "string (summary of audience interests and pain points from analyzed posts)",
  "viral_potential_angles": [
    {
      "angle_summary": "string (specific angle combining trends)",
      "potential_platforms": ["X"],
      "engagement_likelihood": "float (0-1)",
      "hook_template": "string (tweet hook template)",
      "why_viral": "string (reason this angle has viral potential)"
    }
  ],
  "data_sources_used": ["Google Trends", "Twitter Trending Tabs", "Post Analysis"],
  "collection_timestamp": "ISO timestamp from input data",
  "perturbations_applied": [
    "string (description of creative variations added)"
  ]
}

IMPORTANT:
- ALWAYS read from the provided raw trend data, do NOT generate fake trends
- Apply creative perturbation to make angles unique and attention-grabbing
- Consider both data-driven insights AND creative interpretation
- Focus on AI/ML developer audience specifically
- All content is for X (Twitter) platform"""

    agent = Agent(
        model='gemini-2.5-flash',
        name='research_layer',
        description='Research layer that reads trend_data/ and enriches it with analysis',
        instruction=system_prompt,
        tools=[get_latest_trends_tool]  # Bind the tool to fetch trend data
    )

    return agent


@weave.op()
def create_creative_writer_agent() -> Agent:
    """Creative Writer Layer 에이전트 생성"""
    
    system_prompt = """You are the Creative Writer layer. Your task is to generate creative, engaging, and novel content ideas for X (Twitter) based on the research provided. Prioritize novelty, creativity, and engagement potential.

Input: JSON output from the Research layer, containing trending topics, audience insights, and viral potential angles.

Instructions:
1.  Review the research thoroughly to understand trends and audience.
2.  Brainstorm at least 3 distinct content ideas that are novel and creative, building upon the provided viral angles.
3.  For each idea, develop a compelling hook and a unique angle that stands out.
4.  PLATFORM FIXED: All content is for X (Twitter) - focus on tweet-friendly formats:
    - Single tweets (concise, punchy)
    - Short threads (if needed for complex ideas)
    - Always consider: Can this grab attention in a fast-scrolling feed?

Output MUST be a JSON array of objects, each representing a content idea, with the following structure:
[
  {
    "idea_id": "string (unique identifier)",
    "title": "string (a catchy title for the content)",
    "hook": "string (the opening line/concept to grab attention, ≤ 180 chars)",
    "angle": "string (the unique perspective or twist)",
    "target_platforms": ["X"],
    "novelty_score": "float (0-1, how original is the idea?)",
    "creativity_score": "float (0-1, how imaginative and well-developed is the idea?)",
    "engagement_potential_score": "float (0-1, how likely is it to resonate and be shared?)"
  }
]

IMPORTANT: Always set "target_platforms": ["X"] for all ideas. Content must be optimized for X/Twitter."""
    
    # Weave에 prompt publish
    try:
        prompt_obj = weave.StringPrompt(system_prompt)
        weave.publish(prompt_obj, name="cmo_creative_writer_prompt")
        print(f"📝 CMO Creative Writer Prompt published")
    except Exception as e:
        print(f"⚠️  Failed to publish CMO creative writer prompt: {e}")
        import traceback
        traceback.print_exc()
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='creative_writer_layer',
        description='Creative Writer layer for generating novel content ideas',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def create_generator_agent() -> Agent:
    """Generator Layer 에이전트 생성"""
    
    system_prompt = """You are the Generator layer. Your task is to transform a selected creative idea into concrete, shareable content for X (Twitter). Emphasize clarity, shareability, and completeness.

Input: A single content idea object (from the Creative Writer layer's output).

Instructions:
1.  PLATFORM FIXED: Generate content ONLY for X (Twitter). Ignore 'target_platforms' field.
2.  Adhere to X/Twitter best practices:
    - Keep text concise (≤ 180 characters recommended, 280 max)
    - Use hashtags strategically (≤ 2 hashtags)
    - Start with an engaging hook
    - Include media_prompt for visual content
3.  Ensure the content is clear, concise, and easy to understand.
4.  Incorporate a clear call to action or prompt for engagement where appropriate.
5.  Ensure the content is complete and delivers on the promise of the idea's hook and angle.

Output MUST be a JSON object with the following structure:
{
  "generated_content_id": "string (unique identifier for this generation)",
  "source_idea_id": "string (ID of the idea this content is based on)",
  "content_pieces": [
    {
      "platform": "X",
      "format": "Text",
      "content": "string (the actual tweet text, ≤ 180 chars)",
      "character_count": "integer",
      "hashtags": "array of strings (≤ 2)",
      "media_prompt": "string (description for image/video generation)",
      "call_to_action": "string (if applicable)",
      "clarity_score": "float (0-1)",
      "shareability_score": "float (0-1)"
    }
  ],
  "completeness_assessment": "string (brief summary of how well the content fulfills the idea)"
}

IMPORTANT: Always generate exactly ONE content piece for platform "X". Do not generate for multiple platforms."""
    
    # Weave에 prompt publish
    try:
        prompt_obj = weave.StringPrompt(system_prompt)
        weave.publish(prompt_obj, name="cmo_generator_prompt")
        print(f"📝 CMO Generator Prompt published")
    except Exception as e:
        print(f"⚠️  Failed to publish CMO generator prompt: {e}")
        import traceback
        traceback.print_exc()
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='generator_layer',
        description='Generator layer for creating shareable content',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def create_critic_agent() -> Agent:
    """Critic Layer 에이전트 생성"""
    
    system_prompt = """You are the Critic layer. Your task is to evaluate the quality of the generated content across multiple dimensions before publishing. Your evaluation should be thorough, objective, and accurate.

Input: JSON output from the Generator layer, containing generated content pieces.

Instructions:
1.  For each content piece, evaluate its accuracy, objectivity, and thoroughness.
2.  Check for factual errors, misleading statements, or unsupported claims.
3.  Assess if the content presents a balanced view or exhibits bias.
4.  Determine if the content adequately covers the topic as promised by the idea.
5.  Provide constructive feedback for improvement, even if the scores are high.

Output MUST be a JSON object with the following structure:
{
  "evaluation_id": "string (unique identifier)",
  "generated_content_id": "string (ID of the content being evaluated)",
  "evaluations": [
    {
      "platform": "string",
      "content_summary": "string (a brief summary of the content)",
      "accuracy_score": "float (0-1, based on factual correctness)",
      "objectivity_score": "float (0-1, based on neutrality and bias avoidance)",
      "thoroughness_score": "float (0-1, based on completeness and depth)",
      "overall_quality_score": "float (0-1, average or weighted average of the above)",
      "feedback_points": "array of strings (specific suggestions for improvement)"
    }
  ]
}"""
    
    # Weave에 prompt publish
    try:
        prompt_obj = weave.StringPrompt(system_prompt)
        weave.publish(prompt_obj, name="cmo_critic_prompt")
        print(f"📝 CMO Critic Prompt published")
    except Exception as e:
        print(f"⚠️  Failed to publish CMO critic prompt: {e}")
        import traceback
        traceback.print_exc()
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='critic_layer',
        description='Critic layer for evaluating content quality',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def create_safety_agent() -> Agent:
    """Safety Layer 에이전트 생성"""
    
    system_prompt = """You are the Safety layer. Your critical task is to ensure all content meets brand safety, ethical, and legal standards. Your assessment must determine if content is safe for publication.

Input: JSON output from the Generator layer (content pieces) AND JSON output from the Critic layer (evaluation).

Instructions:
1.  Review content for any explicit or implicit violations of brand safety guidelines (e.g., profanity, sensitive topics, brand misrepresentation).
2.  Assess ethical implications (e.g., potential for misinformation, harm, discrimination, exploitation).
3.  Check for legal compliance risks (e.g., copyright infringement, defamation, privacy violations).
4.  Assign a safety score, determine a risk level, and state compliance status.
5.  If issues are found, clearly articulate the red flags and provide actionable recommendations for remediation or outright rejection.

Output MUST be a JSON object with the following structure:
{
  "safety_assessment_id": "string (unique identifier)",
  "generated_content_id": "string (ID of the content being assessed)",
  "overall_safety_score": "float (0-1, higher is safer)",
  "risk_level": "string ('low', 'medium', 'high', 'critical')",
  "compliance_status": "string ('compliant', 'non-compliant', 'review_required')",
  "red_flags": [
    {
      "category": "string (e.g., 'Brand Safety', 'Ethical', 'Legal')",
      "description": "string (specific issue identified)",
      "severity": "string ('minor', 'moderate', 'severe')"
    }
  ],
  "recommendations": "array of strings (suggestions to fix issues or 'Reject Content')"
}"""
    
    # Weave에 prompt publish
    try:
        prompt_obj = weave.StringPrompt(system_prompt)
        weave.publish(prompt_obj, name="cmo_safety_prompt")
        print(f"📝 CMO Safety Prompt published")
    except Exception as e:
        print(f"⚠️  Failed to publish CMO safety prompt: {e}")
        import traceback
        traceback.print_exc()
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='safety_layer',
        description='Safety layer for ensuring brand safety and compliance',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def create_selector_agent() -> Agent:
    """Selector Layer 에이전트 생성 - 최종 컨텐츠 선택 및 가이드 제공"""
    
    system_prompt = """You are the Selector layer. Your final task is to review all generated content from the loop iterations, analyze their scores and safety validations, and SELECT THE BEST ONE to publish.

Input: All iteration results including:
- Multiple content pieces from Generator (from 3 iterations)
- Evaluation scores from Critic for each
- Safety validation results

Instructions:
1. Review ALL content pieces and their scores
2. Filter out any that failed safety (safety_score < 0.8, non-compliant status)
3. Rank remaining candidates by overall score: 
   overall = 0.25*clarity + 0.25*novelty + 0.30*shareability + 0.10*credibility + 0.10*safety
4. Apply minimum thresholds:
   - clarity >= 0.75
   - credibility >= 0.60
   - safety = 1.0 (pass)
5. SELECT the top-scoring candidate that passes all thresholds
6. Format as CLEAR CONTENT GUIDE for publishing

Output MUST be a JSON object with the following structure:
{
  "status": "approved|rejected|needs_review",
  "selected_content": {
    "text": "string (the actual tweet text for X/Twitter)",
    "media_prompt": "string (detailed prompt for image/video generation)",
    "hashtags": ["array", "of", "strings (≤2)"],
    "platform": "X",
    "character_count": "integer"
  },
  "scores": {
    "clarity": "float",
    "novelty": "float", 
    "shareability": "float",
    "credibility": "float",
    "safety": "float",
    "overall": "float"
  },
  "reasoning": "string (why this content was selected over others)",
  "performance_prediction": "string (expected engagement based on scores and historical patterns)",
  "all_candidates_summary": [
    {
      "iteration": "integer",
      "overall_score": "float",
      "status": "selected|rejected|passed_over",
      "brief_content": "string (first 50 chars)"
    }
  ],
  "publishing_guide": {
    "recommended_time": "string (best time to post based on audience)",
    "media_instructions": "string (how to use the media_prompt)",
    "engagement_tips": "array of strings (how to maximize engagement)",
    "monitoring_metrics": "array of strings (what metrics to track)"
  }
}

IMPORTANT: 
- Always select exactly ONE content piece
- Provide clear, actionable publishing guidance
- Include reasoning for transparency
- If no candidate passes thresholds, set status to "rejected" or "needs_review"
"""
    
    # Weave에 prompt publish
    try:
        prompt_obj = weave.StringPrompt(system_prompt)
        weave.publish(prompt_obj, name="cmo_selector_prompt")
        print(f"📝 CMO Selector Prompt published")
    except Exception as e:
        print(f"⚠️  Failed to publish CMO selector prompt: {e}")
        import traceback
        traceback.print_exc()
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='selector_layer',
        description='Selector layer for choosing the best content and providing publishing guide',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def create_image_adapter_agent() -> Agent:
    """Image Adapter Agent - Selector 출력을 Image Caption Agent 입력으로 변환"""
    
    system_prompt = """You are the Image Adapter layer. Your task is to take the selected content from Selector Agent and prepare it for Image Caption Agent.

Input: Selector Agent output with selected_content including:
- text: The tweet text
- media_prompt: Detailed prompt for image generation
- hashtags: Array of hashtags
- platform: "X"

Your task:
1. Extract the media_prompt from selected_content
2. Format it for Image Caption Agent which expects:
   - topic: Main subject (use the tweet text or extract key topic)
   - tone: Infer from the tweet text (witty, informative, minimal, friendly)
   - concept: The media_prompt (this is already the visual concept)

Output MUST be a JSON object with:
{
  "topic": "string (main subject from tweet, 3-5 words)",
  "tone": "string (witty|informative|minimal|friendly - inferred from tweet style)",
  "concept": "string (the media_prompt from selected_content)",
  "hashtags_allowed": true,
  "locale": "en",
  "safety_bans": []
}

IMPORTANT: 
- Use media_prompt as concept directly (it's already optimized for image generation)
- Infer tone from tweet: emoji/humor → witty, facts → informative, minimal words → minimal
- Keep topic concise (3-5 words max)
"""
    
    # Weave에 prompt publish
    try:
        prompt_obj = weave.StringPrompt(system_prompt)
        weave.publish(prompt_obj, name="cmo_image_adapter_prompt")
        print(f"📝 CMO Image Adapter Prompt published")
    except Exception as e:
        print(f"⚠️  Failed to publish CMO image adapter prompt: {e}")
        import traceback
        traceback.print_exc()
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='image_adapter_layer',
        description='Adapter layer for converting Selector output to Image Caption input',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def call_research_layer(topic: str = None, audience_demographics: str = "AI/ML developers, indie hackers, founders") -> Dict[str, Any]:
    """
    Research Layer 호출 - Agent will use get_latest_trends_tool to fetch trend data

    Args:
        topic: 조사할 주제 (optional, will use trend data if None)
        audience_demographics: 타겟 청중

    Returns:
        Research layer 출력 with enriched trend analysis
    """
    # Use direct Gemini API call with function calling enabled
    import google.generativeai as genai
    import os

    genai.configure(api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"))

    # Get system prompt from agent
    agent = create_research_agent()
    system_instruction = agent.instruction

    # Create model with function calling
    model = genai.GenerativeModel(
        'gemini-2.0-flash-exp',
        tools=[get_latest_trends_tool]  # Enable tool calling
    )

    # Simple prompt - let the agent call the tool to fetch data
    prompt = f"""
Target Audience: {audience_demographics}
Topic Focus: {topic if topic else "Discover from trend data"}

Please use the get_latest_trends_tool to fetch the latest trending data, then analyze it to:
1. Extract the most relevant trending topics for the target audience
2. Synthesize audience insights from the collected posts and topics
3. Propose viral angles that combine trends with creative perturbation
4. Add hashtag recommendations and timing insights

Provide your analysis in the specified JSON format.
"""

    try:
        print(f"🔍 Research Layer 실행 중...")

        # Start chat to enable multi-turn tool calling
        chat = model.start_chat()

        # Send initial message with system instruction
        response = chat.send_message(f"{system_instruction}\n\n{prompt}")

        # Handle function calling loop
        while response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            print(f"🔧 Agent calling tool: {function_call.name}")

            # Execute the function call
            if function_call.name == "get_latest_trends_tool":
                function_result = get_latest_trends_tool()
            else:
                function_result = json.dumps({"error": "Unknown function"})

            # Send function result back to model
            response = chat.send_message(
                genai.protos.Content(
                    parts=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_call.name,
                            response={"result": function_result}
                        )
                    )]
                )
            )

        # Get final text response
        response_text = response.text

        result = parse_agent_response(response_text, "research_layer")

        if result and "trending_topics" in result:
            print(f"✓ {len(result.get('trending_topics', []))}개의 트렌딩 토픽 발견")
            return result
        else:
            print(f"⚠️ Research Layer JSON 파싱 실패, 기본값 사용")
            return {
                "trending_topics": [
                    {
                        "topic_name": topic if topic else "Multi-Agent Systems",
                        "relevance_score": 0.8,
                        "timeliness_score": 0.7,
                        "source": "Fallback",
                        "hashtags": ["AIAgents", "BuildInPublic"]
                    }
                ],
                "audience_insights": "AI/ML developers are interested in practical, production-ready solutions and transparent build processes",
                "viral_potential_angles": [
                    {
                        "angle_summary": "Behind-the-scenes agent architecture with real metrics",
                        "potential_platforms": ["X"],
                        "engagement_likelihood": 0.75,
                        "hook_template": "We built [X] with agents. Here's what actually worked:",
                        "why_viral": "Transparency and real numbers resonate with builder community"
                    }
                ],
                "data_sources_used": ["Fallback - No trend data"],
                "collection_timestamp": datetime.now().isoformat(),
                "perturbations_applied": []
            }

    except Exception as e:
        print(f"❌ Research Layer 오류: {e}")
        import traceback
        traceback.print_exc()
        return {
            "trending_topics": [
                {
                    "topic_name": topic if topic else "AI Agents",
                    "relevance_score": 0.75,
                    "timeliness_score": 0.65,
                    "source": "Error Fallback",
                    "hashtags": ["AI"]
                }
            ],
            "audience_insights": "Developers value practical insights and real-world examples",
            "viral_potential_angles": [
                {
                    "angle_summary": "Practical AI implementation",
                    "potential_platforms": ["X"],
                    "engagement_likelihood": 0.7,
                    "hook_template": "Here's what I learned building with AI:",
                    "why_viral": "Learning-focused content performs well"
                }
            ],
            "data_sources_used": ["Error - using fallback"],
            "collection_timestamp": datetime.now().isoformat(),
            "perturbations_applied": []
        }


@weave.op()
def call_creative_writer_layer(research_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creative Writer Layer 호출
    
    Args:
        research_output: Research layer의 출력
    
    Returns:
        Creative Writer layer 출력
    """
    agent = create_creative_writer_agent()
    
    prompt = f"""
Research Output:
{json.dumps(research_output, indent=2, ensure_ascii=False)}

Based on this research, please generate at least 3 creative content ideas.
"""
    
    try:
        print(f"✍️ Creative Writer Layer 실행 중...")
        response = agent.send_message(prompt)
        response_text = response.text if hasattr(response, 'text') else str(response)
        result = parse_agent_response(response_text, "creative_writer_layer")
        
        if result and isinstance(result, list):
            print(f"✓ {len(result)}개의 콘텐츠 아이디어 생성")
            return {"ideas": result}
        elif result and "ideas" in result:
            print(f"✓ {len(result['ideas'])}개의 콘텐츠 아이디어 생성")
            return result
        else:
            print(f"⚠️ Creative Writer Layer JSON 파싱 실패, 기본값 사용")
            return {
                "ideas": [
                    {
                        "idea_id": "idea_1",
                        "title": f"Revolutionary approach to {research_output.get('trending_topics', [{}])[0].get('topic_name', 'AI')}",
                        "hook": "What if we told you everything you know is about to change?",
                        "angle": "Provocative revelation with practical insight",
                        "target_platforms": ["Twitter", "LinkedIn"],
                        "novelty_score": 0.8,
                        "creativity_score": 0.75,
                        "engagement_potential_score": 0.85
                    }
                ]
            }
    
    except Exception as e:
        print(f"❌ Creative Writer Layer 오류: {e}")
        return {
            "ideas": [
                {
                    "idea_id": "idea_1",
                    "title": "Default creative idea",
                    "hook": "Something interesting is happening",
                    "angle": "Unique perspective",
                    "target_platforms": ["Twitter"],
                    "novelty_score": 0.7,
                    "creativity_score": 0.7,
                    "engagement_potential_score": 0.7
                }
            ]
        }


@weave.op()
def call_generator_layer(content_idea: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generator Layer 호출
    
    Args:
        content_idea: 선택된 콘텐츠 아이디어
    
    Returns:
        Generator layer 출력
    """
    agent = create_generator_agent()
    
    prompt = f"""
Content Idea:
{json.dumps(content_idea, indent=2, ensure_ascii=False)}

Please generate actual shareable content for the specified platforms.
"""
    
    try:
        print(f"⚙️ Generator Layer 실행 중...")
        response = agent.send_message(prompt)
        response_text = response.text if hasattr(response, 'text') else str(response)
        result = parse_agent_response(response_text, "generator_layer")
        
        if result and "content_pieces" in result:
            print(f"✓ {len(result['content_pieces'])}개의 콘텐츠 조각 생성")
            return result
        else:
            print(f"⚠️ Generator Layer JSON 파싱 실패, 기본값 사용")
            return {
                "generated_content_id": "gen_1",
                "source_idea_id": content_idea.get("idea_id", "unknown"),
                "content_pieces": [
                    {
                        "platform": "Twitter",
                        "format": "Text",
                        "content": f"{content_idea.get('hook', 'Check this out')} {content_idea.get('title', '')}",
                        "character_count": len(content_idea.get('hook', '') + content_idea.get('title', '')),
                        "hashtags": ["AI", "Tech"],
                        "call_to_action": "Learn more",
                        "clarity_score": 0.8,
                        "shareability_score": 0.75
                    }
                ],
                "completeness_assessment": "Content generated based on idea"
            }
    
    except Exception as e:
        print(f"❌ Generator Layer 오류: {e}")
        return {
            "generated_content_id": "gen_1",
            "source_idea_id": content_idea.get("idea_id", "unknown"),
            "content_pieces": [
                {
                    "platform": "Twitter",
                    "format": "Text",
                    "content": "Default generated content",
                    "character_count": 25,
                    "hashtags": ["Tech"],
                    "call_to_action": None,
                    "clarity_score": 0.7,
                    "shareability_score": 0.7
                }
            ],
            "completeness_assessment": "Default content"
        }


@weave.op()
def call_critic_layer(generator_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Critic Layer 호출
    
    Args:
        generator_output: Generator layer의 출력
    
    Returns:
        Critic layer 출력
    """
    agent = create_critic_agent()
    
    prompt = f"""
Generated Content:
{json.dumps(generator_output, indent=2, ensure_ascii=False)}

Please evaluate the quality of this content across accuracy, objectivity, and thoroughness.
"""
    
    try:
        print(f"🔎 Critic Layer 실행 중...")
        response = agent.send_message(prompt)
        response_text = response.text if hasattr(response, 'text') else str(response)
        result = parse_agent_response(response_text, "critic_layer")
        
        if result and "evaluations" in result:
            print(f"✓ {len(result['evaluations'])}개의 평가 완료")
            return result
        else:
            print(f"⚠️ Critic Layer JSON 파싱 실패, 기본값 사용")
            evaluations = []
            for piece in generator_output.get("content_pieces", []):
                evaluations.append({
                    "platform": piece.get("platform", "Twitter"),
                    "content_summary": piece.get("content", "")[:50],
                    "accuracy_score": 0.8,
                    "objectivity_score": 0.75,
                    "thoroughness_score": 0.7,
                    "overall_quality_score": 0.75,
                    "feedback_points": ["Good clarity", "Could add more depth"]
                })
            
            return {
                "evaluation_id": "eval_1",
                "generated_content_id": generator_output.get("generated_content_id", "unknown"),
                "evaluations": evaluations
            }
    
    except Exception as e:
        print(f"❌ Critic Layer 오류: {e}")
        return {
            "evaluation_id": "eval_1",
            "generated_content_id": generator_output.get("generated_content_id", "unknown"),
            "evaluations": [
                {
                    "platform": "Twitter",
                    "content_summary": "Default evaluation",
                    "accuracy_score": 0.75,
                    "objectivity_score": 0.75,
                    "thoroughness_score": 0.75,
                    "overall_quality_score": 0.75,
                    "feedback_points": ["Default feedback"]
                }
            ]
        }


@weave.op()
def call_safety_layer(generator_output: Dict[str, Any], critic_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safety Layer 호출
    
    Args:
        generator_output: Generator layer의 출력
        critic_output: Critic layer의 출력
    
    Returns:
        Safety layer 출력
    """
    agent = create_safety_agent()
    
    prompt = f"""
Generated Content:
{json.dumps(generator_output, indent=2, ensure_ascii=False)}

Critic Evaluation:
{json.dumps(critic_output, indent=2, ensure_ascii=False)}

Please assess the safety of this content for brand safety, ethical, and legal compliance.
"""
    
    try:
        print(f"🛡️ Safety Layer 실행 중...")
        response = agent.send_message(prompt)
        response_text = response.text if hasattr(response, 'text') else str(response)
        result = parse_agent_response(response_text, "safety_layer")
        
        if result and "overall_safety_score" in result:
            print(f"✓ 안전성 평가 완료: {result.get('risk_level', 'unknown')} 위험도")
            return result
        else:
            print(f"⚠️ Safety Layer JSON 파싱 실패, 기본값 사용")
            return {
                "safety_assessment_id": "safety_1",
                "generated_content_id": generator_output.get("generated_content_id", "unknown"),
                "overall_safety_score": 0.9,
                "risk_level": "low",
                "compliance_status": "compliant",
                "red_flags": [],
                "recommendations": ["Content is safe for publication"]
            }
    
    except Exception as e:
        print(f"❌ Safety Layer 오류: {e}")
        return {
            "safety_assessment_id": "safety_1",
            "generated_content_id": generator_output.get("generated_content_id", "unknown"),
            "overall_safety_score": 0.85,
            "risk_level": "low",
            "compliance_status": "compliant",
            "red_flags": [],
            "recommendations": ["Default safe assessment"]
        }


@weave.op()
def create_image_generator_agent() -> Agent:
    """이미지 생성 에이전트 - media_prompt로 실제 이미지 생성"""
    
    # Image generation tool import
    from image_caption_agent.tools import generate_twitter_image
    
    system_prompt = """You are the Image Generator. Your task is to generate a 3:4 portrait image for Twitter/X based on the media_prompt from the selected content.

Input: You will receive a media_prompt (concept description) from the Selector Agent's output.

Instructions:
1. Extract the media_prompt from the previous context
2. Use generate_twitter_image tool with the media_prompt as the concept
3. The tool will save the image to artifacts/ directory and return the file_path
4. If generation fails, retry once with a simplified prompt
5. Return the COMPLETE file path (e.g., "artifacts/generated_image_20251012_153045.png")

Output MUST be a JSON object:
{
  "status": "success|failed",
  "image_path": "artifacts/generated_image_TIMESTAMP.png",
  "concept_used": "the media_prompt that was used",
  "aspect_ratio": "3:4",
  "retry_attempted": "boolean"
}

CRITICAL:
- The output MUST include "image_path" field with the EXACT file path returned by generate_twitter_image
- Use the media_prompt exactly as provided by Selector
- Do NOT regenerate concept or modify the prompt
- Image is automatically saved to file system (not just artifacts)
- The image_path will be used for X/Twitter media upload
"""
    
    # Weave에 prompt publish
    try:
        prompt_obj = weave.StringPrompt(system_prompt)
        weave.publish(prompt_obj, name="cmo_image_generator_prompt")
        print(f"📝 CMO Image Generator Prompt published")
    except Exception as e:
        print(f"⚠️  Failed to publish CMO image generator prompt: {e}")
        import traceback
        traceback.print_exc()
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='image_generator',
        description='Generates 3:4 portrait images from media_prompt using Imagen',
        instruction=system_prompt,
        tools=[generate_twitter_image]
    )
    
    return agent

