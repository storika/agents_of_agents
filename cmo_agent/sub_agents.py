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


# ===== 서브 에이전트 호출 함수들 =====

@weave.op()
def call_writer_agents(team: SubAgentTeam, topic: str, num_variants: int = 3) -> List[Dict[str, Any]]:
    """
    Writer 에이전트들을 호출하여 콘텐츠 변형 생성
    
    Args:
        team: 서브 에이전트 팀
        topic: 콘텐츠 주제
        num_variants: 생성할 변형 수
    
    Returns:
        생성된 콘텐츠 후보 리스트
    """
    writers = team.get_agents_by_category("writer")
    
    if not writers:
        print("⚠️ Writer 에이전트가 없습니다. 기본 생성 사용")
        return []
    
    variants = []
    
    for i, writer in enumerate(writers):
        if i >= num_variants:
            break
        
        # Writer 에이전트에 콘텐츠 생성 요청
        prompt = f"""
주제: {topic}

요구사항:
- 180자 이하의 트위터 포스트 작성
- 개발자 친화적 톤
- 강력한 hook 포함
- 공유하고 싶게 만드는 메시지

JSON 형식으로 응답:
{{
  "text": "포스트 텍스트",
  "media_prompt": "이미지 생성 프롬프트",
  "hook_strategy": "사용한 hook 전략"
}}
"""
        
        try:
            # ADK Agent 실행
            response = writer.execute(prompt)
            
            # 응답 파싱 (JSON 추출)
            result = parse_agent_response(response, writer.name)
            if result:
                variants.append(result)
        
        except Exception as e:
            print(f"⚠️ {writer.name} 실행 오류: {e}")
    
    return variants


@weave.op()
def call_media_agents(team: SubAgentTeam, text: str, context: str) -> Dict[str, Any]:
    """
    Media 에이전트를 호출하여 미디어 프롬프트 생성
    
    Args:
        team: 서브 에이전트 팀
        text: 콘텐츠 텍스트
        context: 컨텍스트 정보
    
    Returns:
        미디어 생성 정보
    """
    media_agents = team.get_agents_by_category("media")
    
    if not media_agents:
        return {
            "media_prompt": "Modern tech illustration",
            "mode": "image"
        }
    
    media_agent = media_agents[0]
    
    prompt = f"""
콘텐츠: {text}
컨텍스트: {context}

이 콘텐츠에 어울리는 미디어를 제안해주세요.

JSON 형식으로 응답:
{{
  "media_prompt": "상세한 이미지 생성 프롬프트",
  "mode": "image/gif/video",
  "style": "스타일 설명",
  "rationale": "선택 이유"
}}
"""
    
    try:
        response = media_agent.execute(prompt)
        result = parse_agent_response(response, media_agent.name)
        return result if result else {"media_prompt": "Modern tech illustration", "mode": "image"}
    
    except Exception as e:
        print(f"⚠️ {media_agent.name} 실행 오류: {e}")
        return {"media_prompt": "Modern tech illustration", "mode": "image"}


@weave.op()
def call_critic_agents(team: SubAgentTeam, candidate: Dict[str, Any]) -> Dict[str, float]:
    """
    Critic 에이전트를 호출하여 콘텐츠 평가
    
    Args:
        team: 서브 에이전트 팀
        candidate: 평가할 후보
    
    Returns:
        평가 점수 딕셔너리
    """
    critics = team.get_agents_by_category("critic")
    
    if not critics:
        # 기본 평가 사용
        return {
            "clarity": 0.75,
            "novelty": 0.7,
            "shareability": 0.75,
            "credibility": 0.75
        }
    
    critic = critics[0]
    
    prompt = f"""
다음 콘텐츠를 평가해주세요:

텍스트: {candidate['text']}
미디어: {candidate['media_prompt']}

평가 기준 (0.0-1.0):
- clarity: 메시지 명확성
- novelty: 참신성, 독창성
- shareability: 공유 가능성
- credibility: 신뢰도

JSON 형식으로 응답:
{{
  "clarity": 0.85,
  "novelty": 0.75,
  "shareability": 0.9,
  "credibility": 0.8,
  "feedback": "평가 피드백"
}}
"""
    
    try:
        response = critic.execute(prompt)
        result = parse_agent_response(response, critic.name)
        
        if result and all(k in result for k in ["clarity", "novelty", "shareability", "credibility"]):
            return {
                "clarity": float(result["clarity"]),
                "novelty": float(result["novelty"]),
                "shareability": float(result["shareability"]),
                "credibility": float(result["credibility"])
            }
    
    except Exception as e:
        print(f"⚠️ {critic.name} 실행 오류: {e}")
    
    # 기본값 반환
    return {
        "clarity": 0.75,
        "novelty": 0.7,
        "shareability": 0.75,
        "credibility": 0.75
    }


@weave.op()
def call_safety_agents(team: SubAgentTeam, candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safety 에이전트를 호출하여 안전성 검증
    
    Args:
        team: 서브 에이전트 팀
        candidate: 검증할 후보
    
    Returns:
        안전성 평가 결과
    """
    safety_agents = team.get_agents_by_category("safety")
    
    if not safety_agents:
        return {"safety": 1.0, "passed": True, "issues": []}
    
    safety_agent = safety_agents[0]
    
    prompt = f"""
다음 콘텐츠의 안전성을 검증해주세요:

텍스트: {candidate['text']}
미디어: {candidate['media_prompt']}

검증 항목:
- 브랜드 안전성
- 부적절한 내용
- 오해의 소지
- 민감한 주제

JSON 형식으로 응답:
{{
  "safety": 0.95,
  "passed": true,
  "issues": [],
  "recommendations": []
}}
"""
    
    try:
        response = safety_agent.execute(prompt)
        result = parse_agent_response(response, safety_agent.name)
        
        if result and "safety" in result:
            return {
                "safety": float(result["safety"]),
                "passed": result.get("passed", True),
                "issues": result.get("issues", [])
            }
    
    except Exception as e:
        print(f"⚠️ {safety_agent.name} 실행 오류: {e}")
    
    # 기본값 (안전)
    return {"safety": 0.95, "passed": True, "issues": []}


@weave.op()
def call_intelligence_agents(team: SubAgentTeam, iteration_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Intelligence 에이전트들을 호출하여 인사이트 생성
    
    Args:
        team: 서브 에이전트 팀
        iteration_data: 현재 반복 데이터
    
    Returns:
        인사이트 및 추천사항
    """
    intelligence_agents = team.get_agents_by_category("intelligence")
    
    if not intelligence_agents:
        return {"insights": [], "recommendations": []}
    
    insights = []
    
    for agent in intelligence_agents:
        prompt = f"""
현재 반복 데이터:
{json.dumps(iteration_data, indent=2, ensure_ascii=False)}

분석 요청:
- 성능 트렌드
- 개선 기회
- 청중 반응 예측

JSON 형식으로 응답:
{{
  "insights": ["인사이트 1", "인사이트 2"],
  "recommendations": ["추천 1", "추천 2"]
}}
"""
        
        try:
            response = agent.execute(prompt)
            result = parse_agent_response(response, agent.name)
            
            if result:
                insights.extend(result.get("insights", []))
        
        except Exception as e:
            print(f"⚠️ {agent.name} 실행 오류: {e}")
    
    return {"insights": insights, "recommendations": []}


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

