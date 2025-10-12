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

### OpenTelemetry 기반 추적

CMO Agent는 **OpenTelemetry (OTEL)**를 사용하여 Google ADK의 모든 작업을 Weave로 자동 전송합니다:

- ✅ **LLM 호출**: 모든 Gemini 모델 호출 자동 추적
- ✅ **도구 실행**: A2A 프로토콜을 통한 서브 에이전트 호출 추적
- ✅ **워크플로우**: 에이전트 간 데이터 흐름 시각화
- ✅ **타임라인 뷰**: 전체 실행 흐름의 시각화
- ✅ **성능 분석**: 각 단계별 레이턴시 및 비용 분석

### 필수 사항

1. **패키지 설치**:
```bash
pip install google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

2. **환경 변수 설정** (.env 파일 또는 export):
```bash
# 필수: W&B API Key (https://wandb.ai/authorize)
export WANDB_API_KEY=your_wandb_api_key

# 필수: Google API Key
export GOOGLE_API_KEY=your_google_api_key

# 선택: 프로젝트 ID (기본값: mason-choi-storika/WeaveHacks2)
export WANDB_PROJECT_ID=your-entity/your-project
```

⚠️ **중요**: API 키를 코드에 직접 입력하지 마세요! 항상 환경 변수나 `.env` 파일을 사용하세요.

### OTEL 설정 (자동)

CMO Agent를 import하면 자동으로 다음이 설정됩니다:

1. **OTLPSpanExporter**: Weave로 traces 전송
2. **TracerProvider**: ADK의 모든 작업 추적
3. **인증 헤더**: W&B API 키로 자동 인증

```python
# cmo_agent를 import하면 자동으로 OTEL 설정됨
from cmo_agent.agent import root_agent

# 즉시 사용 가능 - 모든 작업이 Weave로 전송됨
response = root_agent.send_message("트렌드 기반 quote tweet 만들어줘")
```

### Weave 대시보드에서 확인

1. **URL 접속**: https://wandb.ai/mason-choi-storika/WeaveHacks2
2. **Traces 탭**: 모든 OTEL traces 확인
3. **Timeline View**: 
   - 각 LLM 호출의 시간과 비용
   - Tool invocation 순서와 결과
   - 에이전트 간 데이터 전달 흐름
4. **비교 분석**: 여러 실행을 비교하여 성능 개선

### 추적되는 데이터

**자동 추적 (OTEL):**
- Agent reasoning steps
- LLM model calls (Gemini)
- Tool executions (A2A protocol)
- Error traces and debugging info

**수동 로깅 (@weave.op):**
- 반복별 후보 점수
- 선택된 콘텐츠
- 예상 vs 실제 engagement
- 시간별 성능 트렌드

### 참고 문서
- [Weave ADK 통합 가이드](https://weave-docs.wandb.ai/guides/integrations/google_adk/)
- [OpenTelemetry Traces to Weave](https://weave-docs.wandb.ai/guides/tracking/tracing)
- [Google ADK Observability](https://google.github.io/adk-docs/observability/weave/)

## 🤝 기여

개선 사항이나 버그 리포트는 환영합니다!

