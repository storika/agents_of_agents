# 🌐 ADK Web UI 실행 가이드

## 실행 방법

```bash
cd /Users/mason/workspace/agents_of_agents
adk web --port 8000 hr_validation_agent
```

브라우저에서 http://localhost:8000 열기

## ✨ Web UI 장점

### 1. 시각적 인터페이스
- 채팅 형식으로 에이전트와 대화
- 입력/출력이 깔끔하게 표시
- JSON 포맷팅 자동

### 2. 예시 프롬프트

#### 빈 팀으로 시작
```
다음 팀 상태를 분석해줘:

{"iteration": 0, "agents": [], "score_history": {"avg_overall": [], "dims_mean": {}, "content_history": []}, "failures": [], "core_roles": ["HRValidation"], "project_goal": "Make Mason viral on Twitter during WeaveHack2", "target_audience": "AI/ML developers, tech founders", "content_focus": "WeaveHack2 progress, AI insights"}
```

#### 성과가 있는 팀
```
다음 팀의 다음 단계를 제안해줘:

{"iteration": 3, "agents": [{"name": "ViralHook", "role": "writer.specialist", "utility": 0.88, "prompt_version": 0, "prompt_similarity": {}, "last_scores": {"clarity": 0.75, "novelty": 0.85, "shareability": 0.92, "overall": 0.84}}], "score_history": {"avg_overall": [0.70, 0.75, 0.84], "dims_mean": {"clarity": 0.75, "novelty": 0.85, "shareability": 0.92}, "content_history": [{"content_id": "tweet_003", "iteration": 3, "contributors": ["ViralHook"], "internal_scores": {"clarity": 0.75, "novelty": 0.85, "shareability": 0.92, "overall": 0.84}, "twitter_likes": 3200, "twitter_retweets": 580, "views": 48000}]}, "project_goal": "Make Mason viral on Twitter", "target_audience": "AI/ML developers", "content_focus": "WeaveHack2"}
```

### 3. Weave 통합 확인

Web UI에서 에이전트를 실행하면:
1. 브라우저 개발자 도구 콘솔에 Weave 링크 표시
2. 터미널에도 `🍩 https://wandb.ai/...` 링크 출력
3. Weave Dashboard에서 실시간 추적 가능

### 4. 반복 테스트가 쉬움

- 이전 대화 기록이 남음
- 같은 입력을 쉽게 재실행
- 다양한 팀 구성 빠르게 테스트

## 📊 Weave에서 볼 수 있는 것

### Call Details
- **Input**: 전체 team_state JSON
- **Output**: HR 결정 (hire_plan, merge_plan, etc.)
- **Duration**: 실행 시간
- **LLM Calls**: 내부적으로 호출된 LLM 수

### Call Graph
```
analyze_team_and_decide
├── generate_hire_plan
│   └── ideate_initial_team (LLM)
├── identify_merge_candidates
├── identify_prune_candidates
└── generate_prompt_feedback
```

### Traces
- 모든 에이전트 실행 시계열
- 성능 병목 지점 파악
- 에러 발생 위치 추적

## 🎯 사용 시나리오

### Scenario 1: Bootstrap (빈 팀)
```
User: Mason을 바이럴시킬 초기 팀을 구성해줘
Agent: [analyze_team_and_decide 호출]
Result: 
  - TweetCrafter (writer)
  - TrendAnalyzer (analyzer)
  - EngageCritic (critic)
  - HRValidation (critic)
```

### Scenario 2: 성과 개선
```
User: novelty가 낮은데(0.52), 어떤 에이전트를 추가해야 할까?
Agent: [LLM이 팀 분석]
Result:
  - 채용: ContrarianTake (writer) - 신선한 관점 제공
  - 코칭: 기존 writer에게 "더 대담한 주장" 피드백
```

### Scenario 3: 바이럴 성공 분석
```
User: 이 트윗이 48,000 views를 받았어. 어떤 에이전트가 기여했을까?
Agent: [content_history 분석]
Result:
  - ViralHook의 기여도가 높음 (shareability: 0.92)
  - 유사한 에이전트 추가 제안
```

## 🐛 트러블슈팅

### Port 충돌
```bash
# 다른 포트 사용
adk web --port 8080 hr_validation_agent
```

### Weave 링크가 안 보임
```bash
# .env 파일 확인
cat .env | grep WANDB_API_KEY

# 없으면 추가
echo "WANDB_API_KEY=your-key" >> .env
```

### JSON 파싱 에러
- Web UI에서 JSON을 한 줄로 입력
- 또는 Python 코드로 감싸기:
```python
import json
team_state = {...}
print(json.dumps(team_state))
```

## 🔗 유용한 링크

- **Weave Dashboard**: https://wandb.ai/mason-choi-storika/WeaveHacks2/weave
- **ADK Docs**: https://google.github.io/adk-docs/
- **Weave Docs**: https://wandb.github.io/weave/

---

**Happy Agent Building! 🚀🐝**

