# 🔄 Iteration Flow - Input/Output 명세

## Overview

각 Iteration은 다음 순서로 진행됩니다:
```
Input (team_state.json)
    ↓
HR Agent 분석
    ↓
Output (hr_decisions.json)
    ↓
결정 적용 (에이전트 생성/제거/수정)
    ↓
에이전트들이 콘텐츠 생성
    ↓
Twitter 발행 & 메트릭 수집
    ↓
다음 Iteration Input 준비
```

---

## Iteration 0: Bootstrap (빈 팀 시작)

### Input: `team_state.json`

```json
{
  "iteration": 0,
  "agents": [],
  "score_history": {
    "avg_overall": [],
    "dims_mean": {},
    "content_history": []
  },
  "failures": [],
  "core_roles": ["HRValidation"],
  
  "project_goal": "Make Mason viral on Twitter during WeaveHack2",
  "target_audience": "AI/ML developers, tech founders, WeaveHack2 participants",
  "content_focus": "WeaveHack2 progress, AI agent insights, viral tech takes"
}
```

### Output: `hr_decisions.json`

```json
{
  "hire_plan": [
    {
      "name": "ViralHook",
      "role": "writer.specialist",
      "system_prompt": "You are ViralHook, specialist in creating attention-grabbing tweet openings. Your mission: Write the first 1-2 lines of every tweet to maximize click-through and engagement. Study viral patterns: controversy, curiosity gaps, bold claims, surprising stats. Always hook within 280 characters. Safety: No misleading clickbait or false claims.",
      "reason": "Bootstrap: Essential for high shareability and engagement",
      "config": {
        "model": "gemini-2.5-flash",
        "temperature": 0.8,
        "max_tokens": 512
      },
      "tools": []
    },
    {
      "name": "TrendScout",
      "role": "analyzer.specialist",
      "system_prompt": "You are TrendScout, who monitors Twitter trends in AI/ML space. Your mission: Identify trending topics, viral discussions, and emerging narratives that Mason should engage with. Provide real-time trend analysis with engagement predictions. Focus: WeaveHack2, AI agents, LLM developments. Output: JSON with {topic, engagement_potential, angle}.",
      "reason": "Bootstrap: Ensures content is timely and relevant",
      "config": {
        "model": "gemini-2.5-flash",
        "temperature": 0.3,
        "max_tokens": 1024
      },
      "tools": ["twitter_search", "trend_analysis"]
    },
    {
      "name": "EngageCritic",
      "role": "critic.specialist",
      "system_prompt": "You are EngageCritic, the quality guardian. Your mission: Evaluate every piece of content before posting. Score across 5 dimensions (clarity, novelty, shareability, credibility, safety) on 0-1 scale. Provide actionable feedback. Reject content below 0.6 overall. Output: JSON with scores and feedback.",
      "reason": "Bootstrap: Quality control and feedback loop",
      "config": {
        "model": "gemini-2.5-flash",
        "temperature": 0.2,
        "max_tokens": 512
      },
      "tools": []
    }
  ],
  "merge_plan": [],
  "prune_list": [],
  "prompt_feedback": [],
  "policies": {
    "team_cap": 8,
    "utility_floor": 0.35,
    "sim_threshold": 0.80,
    "spawn_cooldown": 1
  }
}
```

### Action: 에이전트 생성

```python
from google.adk.agents.llm_agent import Agent

for hire in hr_decisions["hire_plan"]:
    agent_spec = hire  # 이미 완전한 스펙
    
    agent = Agent(
        model=agent_spec["config"]["model"],
        name=agent_spec["name"],
        description=f"{agent_spec['role']} - {agent_spec['reason']}",
        instruction=agent_spec["system_prompt"],
        # tools는 필요시 추가
    )
    
    # 저장
    agents[agent_spec["name"]] = agent
```

---

## Iteration 1: 첫 번째 콘텐츠 생성

### 콘텐츠 생성 프로세스

```python
# 1. TrendScout가 트렌드 분석
trends = agents["TrendScout"].run("Analyze current AI/ML trends on Twitter")

# 2. ViralHook이 훅 생성
hook = agents["ViralHook"].run(f"Create a viral hook for: {trends['top_topic']}")

# 3. 다른 writer들이 본문 작성
# ...

# 4. EngageCritic이 평가
evaluation = agents["EngageCritic"].run(f"Evaluate this content: {content}")

# 5. 평가 통과하면 발행
if evaluation["overall"] >= 0.6:
    tweet_id = post_to_twitter(content)
```

### 메트릭 수집 (24-48시간 후)

```python
import time
from twitter_api import get_tweet_metrics

time.sleep(48 * 3600)  # 48시간 대기

metrics = get_tweet_metrics(tweet_id)
# {
#   "twitter_likes": 180,
#   "twitter_retweets": 12,
#   "twitter_replies": 8,
#   "views": 2100,
#   "click_through_rate": 0.04
# }
```

### Next Iteration Input: `team_state.json`

```json
{
  "iteration": 1,
  "agents": [
    {
      "name": "ViralHook",
      "role": "writer.specialist",
      "utility": 0.68,
      "prompt_version": 0,
      "prompt_similarity": {},
      "last_scores": {
        "clarity": 0.75,
        "novelty": 0.60,
        "shareability": 0.85,
        "credibility": 0.65,
        "safety": 0.95,
        "overall": 0.76
      }
    },
    {
      "name": "TrendScout",
      "role": "analyzer.specialist",
      "utility": 0.72,
      "prompt_version": 0,
      "prompt_similarity": {},
      "last_scores": {
        "clarity": 0.90,
        "novelty": 0.70,
        "shareability": 0.60,
        "credibility": 0.85,
        "safety": 1.0,
        "overall": 0.81
      }
    },
    {
      "name": "EngageCritic",
      "role": "critic.specialist",
      "utility": 0.75,
      "prompt_version": 0,
      "prompt_similarity": {},
      "last_scores": {
        "clarity": 0.95,
        "novelty": 0.65,
        "shareability": 0.70,
        "credibility": 0.90,
        "safety": 1.0,
        "overall": 0.84
      }
    }
  ],
  "score_history": {
    "avg_overall": [0.72],
    "dims_mean": {
      "clarity": 0.87,
      "novelty": 0.65,
      "shareability": 0.72,
      "credibility": 0.80,
      "safety": 0.98
    },
    "content_history": [
      {
        "content_id": "tweet_001",
        "iteration": 1,
        "contributors": ["ViralHook", "TrendScout", "EngageCritic"],
        "internal_scores": {
          "clarity": 0.75,
          "novelty": 0.60,
          "shareability": 0.85,
          "credibility": 0.65,
          "safety": 0.95,
          "overall": 0.76
        },
        "twitter_likes": 180,
        "twitter_retweets": 12,
        "twitter_replies": 8,
        "views": 2100,
        "click_through_rate": 0.04
      }
    ]
  },
  "failures": [],
  "core_roles": ["HRValidation", "EngageCritic"],
  "project_goal": "Make Mason viral on Twitter during WeaveHack2",
  "target_audience": "AI/ML developers, tech founders, WeaveHack2 participants",
  "content_focus": "WeaveHack2 progress, AI agent insights, viral tech takes"
}
```

---

## Iteration 2+: 성과 기반 최적화

### HR Agent 분석

```python
# HR Agent가 분석할 내용:
# 1. novelty가 낮음 (0.65) → 전문가 채용 필요
# 2. 외부 메트릭 (engagement rate = 9.5%) 양호하지만 viral은 아님
# 3. 모든 에이전트 utility > 0.35 → 제거 불필요
```

### Output: `hr_decisions.json`

```json
{
  "hire_plan": [
    {
      "name": "ContrarianTake",
      "role": "writer.specialist",
      "system_prompt": "You are ContrarianTake, specialist in provocative yet insightful perspectives. Your mission: Challenge conventional wisdom in AI/ML with well-reasoned contrarian views. Find the unpopular truth, the overlooked angle, the 'everyone is wrong about X' take. Balance: controversial enough to spark discussion, credible enough to be taken seriously. Safety: No personal attacks or inflammatory language.",
      "reason": "Improve novelty dimension (current: 0.65 → target: 0.80+)",
      "config": {
        "model": "gemini-2.5-flash",
        "temperature": 0.9,
        "max_tokens": 512
      },
      "tools": []
    }
  ],
  "merge_plan": [],
  "prune_list": [],
  "prompt_feedback": [
    {
      "agent": "ViralHook",
      "suggestion": "Add more data-driven hooks. Rule 1: Include surprising statistics. Rule 2: Use specific numbers (e.g., '23%' not 'many'). Example: 'AI agents reduced our tweet writing time by 73%. Here's how...'"
    }
  ],
  "policies": {
    "team_cap": 8,
    "utility_floor": 0.35,
    "sim_threshold": 0.80,
    "spawn_cooldown": 1
  }
}
```

---

## Input Schema (완전 명세)

```typescript
interface TeamState {
  iteration: number;  // 0부터 시작
  
  agents: Agent[];
  
  score_history: {
    avg_overall: number[];  // Iteration별 평균 overall 점수
    dims_mean: {
      clarity: number;
      novelty: number;
      shareability: number;
      credibility: number;
      safety: number;
    };
    content_history: ContentPerformance[];  // 최신순
  };
  
  failures: string[];  // 이전 실패 사례 (학습용)
  core_roles: string[];  // 제거 불가 에이전트 이름
  
  // 프로젝트 컨텍스트 (초기 설정, 변경 가능)
  project_goal: string;
  target_audience: string;
  content_focus: string;
}

interface Agent {
  name: string;
  role: "writer.specialist" | "designer.specialist" | "critic.specialist" 
      | "analyzer.specialist" | "coordinator.specialist" | "engager.specialist";
  utility: number;  // 0-1, EMA of content performance
  prompt_version: number;
  prompt_similarity: { [agentName: string]: number };  // 0-1
  last_scores: {
    clarity: number;
    novelty: number;
    shareability: number;
    credibility: number;
    safety: number;
    overall: number;
  };
}

interface ContentPerformance {
  content_id: string;
  iteration: number;
  contributors: string[];  // 이 콘텐츠에 기여한 에이전트 이름들
  
  internal_scores: {
    clarity: number;
    novelty: number;
    shareability: number;
    credibility: number;
    safety: number;
    overall: number;
  };
  
  // Twitter metrics (optional, 24-48시간 후 업데이트)
  twitter_likes?: number;
  twitter_retweets?: number;
  twitter_replies?: number;
  linkedin_reactions?: number;
  linkedin_shares?: number;
  reddit_upvotes?: number;
  reddit_comments?: number;
  views?: number;
  click_through_rate?: number;  // 0-1
}
```

---

## Output Schema (완전 명세)

```typescript
interface HRDecision {
  hire_plan: HirePlan[];
  merge_plan: MergePlan[];
  prune_list: PruneItem[];
  prompt_feedback: PromptFeedback[];
  policies: Policies;
}

interface HirePlan {
  name: string;
  role: AgentRole;
  system_prompt: string;  // ADK-compatible instruction
  reason: string;
  
  config: {
    model: string;  // e.g., "gemini-2.5-flash"
    temperature: number;  // 0-1
    max_tokens: number;
  };
  
  tools: string[];  // Tool names (e.g., ["twitter_search", "trend_analysis"])
}

interface MergePlan {
  a: string;  // Agent name
  b: string;  // Agent name
  reason: string;
}

interface PruneItem {
  name: string;
  reason: string;
}

interface PromptFeedback {
  agent: string;
  suggestion: string;  // Specific, actionable improvement
}

interface Policies {
  team_cap: number;        // 8
  utility_floor: number;   // 0.35
  sim_threshold: number;   // 0.80
  spawn_cooldown: number;  // 1
}
```

---

## 에이전트 생성 헬퍼 (Python)

```python
from google.adk.agents.llm_agent import Agent
from typing import Dict, List

def create_agent_from_hire_plan(hire_plan: Dict) -> Agent:
    """
    HR Agent의 hire_plan을 실제 ADK Agent로 변환.
    
    Args:
        hire_plan: HirePlan 딕셔너리
    
    Returns:
        Agent 인스턴스
    """
    config = hire_plan.get("config", {})
    
    agent = Agent(
        model=config.get("model", "gemini-2.5-flash"),
        name=hire_plan["name"],
        description=f"{hire_plan['role']} - {hire_plan['reason']}",
        instruction=hire_plan["system_prompt"],
        # tools는 별도로 등록 필요
    )
    
    return agent


def apply_hr_decisions(
    current_agents: Dict[str, Agent],
    hr_decisions: Dict
) -> Dict[str, Agent]:
    """
    HR 결정을 실제 에이전트 팀에 적용.
    
    Args:
        current_agents: 현재 에이전트 딕셔너리 {name: Agent}
        hr_decisions: HR Agent의 결정
    
    Returns:
        업데이트된 에이전트 딕셔너리
    """
    # 1. Hire
    for hire in hr_decisions["hire_plan"]:
        print(f"[HIRE] {hire['name']} ({hire['role']})")
        current_agents[hire["name"]] = create_agent_from_hire_plan(hire)
    
    # 2. Prune
    for prune in hr_decisions["prune_list"]:
        print(f"[PRUNE] {prune['name']}: {prune['reason']}")
        if prune["name"] in current_agents:
            del current_agents[prune["name"]]
    
    # 3. Merge (TODO: 병합 로직 구현)
    for merge in hr_decisions["merge_plan"]:
        print(f"[MERGE] {merge['a']} + {merge['b']}")
        # 두 에이전트의 capabilities 병합
    
    # 4. Coach (프롬프트 업데이트)
    for feedback in hr_decisions["prompt_feedback"]:
        if feedback["agent"] in current_agents:
            print(f"[COACH] {feedback['agent']}: {feedback['suggestion'][:50]}...")
            # 프롬프트에 피드백 반영
            agent = current_agents[feedback["agent"]]
            updated_instruction = f"{agent.instruction}\n\nCoaching Feedback: {feedback['suggestion']}"
            # Re-create agent with updated prompt
    
    return current_agents
```

---

## 전체 루프 예시

```python
import json
from hr_validation_agent.agent import analyze_team_and_decide

# Initialize
with open("examples/mason_weavehack2_empty.json") as f:
    team_state = json.load(f)

agents = {}

for iteration in range(100):
    print(f"\n{'='*70}")
    print(f"Iteration {iteration}")
    print(f"{'='*70}\n")
    
    # 1. HR Agent 실행
    team_state["iteration"] = iteration
    result = analyze_team_and_decide(json.dumps(team_state))
    hr_decisions = json.loads(result)
    
    # 2. 결정 적용
    agents = apply_hr_decisions(agents, hr_decisions)
    
    # 3. 콘텐츠 생성
    content, internal_scores = generate_content_with_agents(agents)
    
    # 4. Twitter 발행
    tweet_id = post_to_twitter(content)
    
    # 5. 메트릭 수집 (48시간 후)
    time.sleep(48 * 3600)
    external_metrics = get_tweet_metrics(tweet_id)
    
    # 6. team_state 업데이트
    content_performance = {
        "content_id": f"tweet_{iteration:03d}",
        "iteration": iteration,
        "contributors": list(agents.keys()),
        "internal_scores": internal_scores,
        **external_metrics
    }
    team_state["score_history"]["content_history"].insert(0, content_performance)
    
    # 7. Agent utility 업데이트
    for agent_name in agents:
        team_state["agents"] = update_agent_utility(agent_name, content_performance)
```

---

**버전**: 1.0.0  
**업데이트**: 2025-10-11

