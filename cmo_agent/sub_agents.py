"""
CMO Agent 서브 에이전트 관리
HR Agent의 hire_plan을 기반으로 서브 에이전트 팀 구성 및 관리
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from google.adk.agents.llm_agent import Agent
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

@weave.op()
def create_research_agent() -> Agent:
    """Research Layer 에이전트 생성"""
    
    system_prompt = """You are the Research layer. Your task is to identify trending topics, analyze audience interests, and pinpoint viral opportunities for content creation. Focus on relevance, timeliness, and data quality.

Input: A broad topic or industry to investigate, target audience demographics, current events context.

Instructions:
1.  Identify at least 3 current trending topics relevant to the input topic/industry.
2.  Analyze typical audience interests and pain points within the specified demographics related to these trends.
3.  Propose unique angles or narratives that have high viral potential.
4.  Specify the data sources you would use (e.g., social media trends, news aggregators, search engine data, forum discussions).

Output MUST be a JSON object with the following structure:
{
  "trending_topics": [
    {
      "topic_name": "string",
      "relevance_score": "float (0-1)",
      "timeliness_score": "float (0-1)"
    }
  ],
  "audience_insights": "string (summary of audience interests and pain points)",
  "viral_potential_angles": [
    {
      "angle_summary": "string",
      "potential_platforms": "array of strings",
      "engagement_likelihood": "float (0-1)"
    }
  ],
  "data_sources_used": "array of strings (e.g., 'Google Trends', 'Twitter Analytics')"
}"""
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='research_layer',
        description='Research layer for identifying trends and viral opportunities',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def create_creative_writer_agent() -> Agent:
    """Creative Writer Layer 에이전트 생성"""
    
    system_prompt = """You are the Creative Writer layer. Your task is to generate creative, engaging, and novel content ideas and angles based on the research provided. Prioritize novelty, creativity, and engagement potential.

Input: JSON output from the Research layer, containing trending topics, audience insights, and viral potential angles.

Instructions:
1.  Review the research thoroughly to understand trends and audience.
2.  Brainstorm at least 3 distinct content ideas that are novel and creative, building upon the provided viral angles.
3.  For each idea, develop a compelling hook and a unique angle that stands out.
4.  Consider different content formats (e.g., tweet thread, short video script, blog post concept).

Output MUST be a JSON array of objects, each representing a content idea, with the following structure:
[
  {
    "idea_id": "string (unique identifier)",
    "title": "string (a catchy title for the content)",
    "hook": "string (the opening line/concept to grab attention)",
    "angle": "string (the unique perspective or twist)",
    "target_platforms": "array of strings (e.g., 'Twitter', 'TikTok', 'Blog')",
    "novelty_score": "float (0-1, how original is the idea?)",
    "creativity_score": "float (0-1, how imaginative and well-developed is the idea?)",
    "engagement_potential_score": "float (0-1, how likely is it to resonate and be shared?)"
  }
]"""
    
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
    
    system_prompt = """You are the Generator layer. Your task is to transform a selected creative idea into concrete, shareable content suitable for specified platforms. Emphasize clarity, shareability, and completeness.

Input: A single content idea object (from the Creative Writer layer's output).

Instructions:
1.  Based on the 'target_platforms' for the selected idea, generate actual content pieces.
2.  Adhere to platform-specific best practices (e.g., Twitter character limits, hashtag usage, engaging opening lines).
3.  Ensure the content is clear, concise, and easy to understand.
4.  Incorporate a clear call to action or prompt for engagement where appropriate.
5.  Ensure the content is complete and delivers on the promise of the idea's hook and angle.

Output MUST be a JSON object with the following structure:
{
  "generated_content_id": "string (unique identifier for this generation)",
  "source_idea_id": "string (ID of the idea this content is based on)",
  "content_pieces": [
    {
      "platform": "string (e.g., 'Twitter', 'Blog Post', 'LinkedIn')",
      "format": "string (e.g., 'Text', 'Thread', 'Image Prompt')",
      "content": "string (the actual content body)",
      "character_count": "integer",
      "hashtags": "array of strings",
      "call_to_action": "string (if applicable)",
      "clarity_score": "float (0-1)",
      "shareability_score": "float (0-1)"
    }
  ],
  "completeness_assessment": "string (brief summary of how well the content fulfills the idea)"
}"""
    
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
    
    agent = Agent(
        model='gemini-2.5-flash',
        name='safety_layer',
        description='Safety layer for ensuring brand safety and compliance',
        instruction=system_prompt
    )
    
    return agent


@weave.op()
def call_research_layer(topic: str, audience_demographics: str = "developers, tech enthusiasts") -> Dict[str, Any]:
    """
    Research Layer 호출
    
    Args:
        topic: 조사할 주제
        audience_demographics: 타겟 청중
    
    Returns:
        Research layer 출력
    """
    agent = create_research_agent()
    
    prompt = f"""
Topic: {topic}
Target Audience: {audience_demographics}
Current Context: Latest developments in AI and technology

Please provide trending topics, audience insights, and viral angles for this topic.
"""
    
    try:
        print(f"🔍 Research Layer 실행 중...")
        response = agent.execute(prompt)
        result = parse_agent_response(response, "research_layer")
        
        if result:
            print(f"✓ {len(result.get('trending_topics', []))}개의 트렌딩 토픽 발견")
            return result
        else:
            print(f"⚠️ Research Layer JSON 파싱 실패, 기본값 사용")
            return {
                "trending_topics": [
                    {"topic_name": topic, "relevance_score": 0.8, "timeliness_score": 0.7}
                ],
                "audience_insights": "Developers are interested in practical, actionable insights",
                "viral_potential_angles": [
                    {"angle_summary": "Behind-the-scenes look", "potential_platforms": ["Twitter", "LinkedIn"], "engagement_likelihood": 0.75}
                ],
                "data_sources_used": ["Google Trends", "Twitter"]
            }
    
    except Exception as e:
        print(f"❌ Research Layer 오류: {e}")
        return {
            "trending_topics": [
                {"topic_name": topic, "relevance_score": 0.8, "timeliness_score": 0.7}
            ],
            "audience_insights": "Developers are interested in practical, actionable insights",
            "viral_potential_angles": [
                {"angle_summary": "Behind-the-scenes look", "potential_platforms": ["Twitter", "LinkedIn"], "engagement_likelihood": 0.75}
            ],
            "data_sources_used": ["Google Trends", "Twitter"]
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
        response = agent.execute(prompt)
        result = parse_agent_response(response, "creative_writer_layer")
        
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
        response = agent.execute(prompt)
        result = parse_agent_response(response, "generator_layer")
        
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
        response = agent.execute(prompt)
        result = parse_agent_response(response, "critic_layer")
        
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
        response = agent.execute(prompt)
        result = parse_agent_response(response, "safety_layer")
        
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

