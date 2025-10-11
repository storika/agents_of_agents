# CMO Agent (Chief Marketing Orchestrator)

소셜 미디어 콘텐츠 생성, 평가, 발행을 조율하는 마케팅 오케스트레이터 에이전트입니다.

## 🎯 주요 기능

- **4단계 프로세스**
  1. **Research Stage**: 트렌드 조사 및 키워드 발견
  2. **Generate Stage**: 3-6개의 콘텐츠 후보 생성
  3. **Evaluate Stage**: Critic + Safety 에이전트로 평가
  4. **Select & Publish Stage**: 최고 후보 선택 및 발행

- **멀티모달 콘텐츠**: 텍스트 + 이미지/비디오 프롬프트 페어링
- **안전성 필터**: safety >= 0.8 기준으로 필터링
- **Weave 통합**: 모든 메트릭 자동 로깅

## 📦 설치

```bash
# 프로젝트 루트에서
pip install -r requirements.txt
```

## 🚀 사용 방법

### 1. Python 코드에서 사용

```python
from cmo_agent.agent import orchestrate_content_creation, run_cmo_iteration
import json

# 방법 1: 직접 호출
result = orchestrate_content_creation(
    iteration=0,
    topic="AI agents that hire other AI agents",
    num_candidates=5
)

result_dict = json.loads(result)
print(result_dict["selected"]["text"])

# 방법 2: 설정 기반 실행
config = {
    "iteration": 1,
    "topic": "WeaveHack2 프로젝트",
    "num_candidates": 4
}

result = run_cmo_iteration(json.dumps(config))
```

### 2. 커맨드라인에서 실행

```bash
# 기본 실행
python -m cmo_agent.agent

# 커스텀 토픽
python -m cmo_agent.agent "AI agents revolutionizing developer workflow"
```

### 3. ADK Agent로 대화형 사용

```python
from cmo_agent.agent import root_agent

# 자연어로 요청
response = root_agent.execute(
    "AI 에이전트에 대한 트위터 콘텐츠를 5개 만들어주세요."
)
```

## 📊 출력 형식

```json
{
  "iteration": 0,
  "candidates": [
    {
      "text": "We built an AI that hires other AIs.",
      "media_prompt": "3D isometric illustration of agents recruiting each other.",
      "mode": "image",
      "scores": {
        "clarity": 0.9,
        "novelty": 0.8,
        "shareability": 0.88,
        "credibility": 0.75,
        "safety": 1.0,
        "overall": 0.86
      }
    }
  ],
  "selected": {
    "text": "We built an AI that hires other AIs.",
    "media_prompt": "3D isometric illustration of agents recruiting each other.",
    "mode": "image",
    "expected_overall": 0.86
  },
  "publish_status": "queued",
  "feedback_summary": "Top performer: high clarity & novelty, safe tone, developer appeal."
}
```

## 🔧 사용 가능한 도구

| 도구 | 설명 |
|------|------|
| `research_trends()` | 트렌드 조사 및 키워드 발견 |
| `generate_content_candidate()` | 콘텐츠 후보 생성 |
| `evaluate_content()` | Critic + Safety 평가 |
| `x_publish()` | Twitter/X 발행 |
| `save_iteration_metrics()` | Weave에 메트릭 로깅 |
| `orchestrate_content_creation()` | 전체 프로세스 실행 |
| `run_cmo_iteration()` | 설정 기반 실행 |

## 📈 평가 기준

- **clarity** (25%): 메시지 명확성
- **novelty** (25%): 참신성, 독창성
- **shareability** (30%): 공유 가능성, 바이럴 잠재력
- **credibility** (10%): 신뢰도
- **safety** (10%): 안전성 (최소 0.8 필요)

## 🧪 테스트

```bash
# 전체 테스트 실행
python test_cmo_agent.py

# 특정 테스트만
python -c "from test_cmo_agent import test_basic_orchestration; test_basic_orchestration()"
```

## 🔄 HR Agent와 통합

CMO는 HR Agent의 결정에 따라 서브 에이전트 팀을 자동으로 조정합니다:

```python
# HR 결정 적용
hr_decisions = json.loads(hr_agent_result)
cmo_config = {
    "iteration": 5,
    "topic": "AI automation",
    "num_candidates": 6,
    "hr_guidelines": hr_decisions  # HR 피드백 반영
}

result = run_cmo_iteration(json.dumps(cmo_config))
```

## 🌟 스타일 가이드

- **톤**: 대화형, 개발자 친화적
- **길이**: 180자 이하 (Twitter 최적화)
- **형식**: 항상 텍스트 + 미디어 프롬프트 페어
- **안전성**: 모든 콘텐츠는 safety >= 0.8 필수

## 📝 예제

### 예제 1: 기본 콘텐츠 생성
```python
result = orchestrate_content_creation(
    iteration=0,
    topic="AI agents",
    num_candidates=3
)
```

### 예제 2: 고급 설정
```python
config = {
    "iteration": 10,
    "topic": "Self-improving AI teams",
    "num_candidates": 6,
    "research_file": "research.json",
    "team_state_file": "team_state_iteration_010.json",
    "last_iteration_file": "last_iteration.json"
}

result = run_cmo_iteration(json.dumps(config))
```

## 🐝 Weave 대시보드

모든 메트릭은 자동으로 Weave에 로깅됩니다:
- 반복별 후보 점수
- 선택된 콘텐츠
- 예상 vs 실제 engagement
- 시간별 성능 트렌드

Weave 프로젝트: `mason-choi-storika/WeaveHacks2`

## 🤝 기여

개선 사항이나 버그 리포트는 환영합니다!

