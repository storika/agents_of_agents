# CMO Agent - Weave OpenTelemetry 설정 가이드

이 가이드는 CMO Agent를 Weave와 통합하여 Google ADK traces를 자동으로 추적하는 방법을 설명합니다.

## 📚 참고 문서

- [Weave ADK Integration](https://weave-docs.wandb.ai/guides/integrations/google_adk/)
- [Send OTEL Traces to Weave](https://weave-docs.wandb.ai/guides/tracking/tracing)
- [Google ADK Observability](https://google.github.io/adk-docs/observability/weave/)

## 🎯 개요

CMO Agent는 **OpenTelemetry (OTEL)**를 사용하여 다음을 자동으로 추적합니다:

- ✅ **LLM 호출**: 모든 Gemini 모델 호출 (latency, cost, tokens)
- ✅ **Tool 실행**: A2A 프로토콜을 통한 서브 에이전트 호출
- ✅ **워크플로우**: 에이전트 간 데이터 흐름
- ✅ **에러 추적**: 실패한 호출과 디버깅 정보

## 📋 필수 사항

### 1. 패키지 설치

```bash
pip install google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

### 2. 환경 변수 설정

#### 옵션 A: .env 파일 사용 (권장)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```bash
# Weave (W&B) Configuration
# API Key: https://wandb.ai/authorize
WANDB_API_KEY=your_wandb_api_key_here

# W&B Project (entity/project format)
# 기본값: mason-choi-storika/WeaveHacks2
WANDB_PROJECT_ID=your-entity/your-project

# Google API Key for Gemini models
GOOGLE_API_KEY=your_google_api_key_here
```

#### 옵션 B: 환경 변수 export

```bash
export WANDB_API_KEY=your_wandb_api_key
export WANDB_PROJECT_ID=your-entity/your-project
export GOOGLE_API_KEY=your_google_api_key
```

### 3. API Key 획득

#### W&B API Key
1. https://wandb.ai/authorize 접속
2. API Key 복사
3. `WANDB_API_KEY`에 설정

#### Google API Key
1. Google AI Studio (https://aistudio.google.com/app/apikey) 접속
2. API Key 생성
3. `GOOGLE_API_KEY`에 설정

## 🚀 사용 방법

### 자동 설정

CMO Agent를 import하면 OpenTelemetry가 **자동으로 설정**됩니다:

```python
# 이 import만으로 OTEL이 자동 설정됨
from cmo_agent.agent import root_agent, decide_and_execute

# 즉시 사용 가능 - 모든 작업이 Weave로 전송됨
response = decide_and_execute("트렌드 기반 quote tweet 만들어줘")
```

### 내부 동작

`cmo_agent/agent.py`가 자동으로 수행하는 작업:

1. **환경 변수 로드**
   ```python
   WANDB_API_KEY = os.environ.get("WANDB_API_KEY")
   PROJECT_ID = os.environ.get("WANDB_PROJECT_ID", "mason-choi-storika/WeaveHacks2")
   ```

2. **OTEL Exporter 설정**
   ```python
   exporter = OTLPSpanExporter(
       endpoint="https://trace.wandb.ai/otel/v1/traces",
       headers={
           "Authorization": f"Basic {AUTH}",
           "project_id": PROJECT_ID,
       }
   )
   ```

3. **Tracer Provider 설정** (ADK import 전에 수행)
   ```python
   tracer_provider = trace_sdk.TracerProvider()
   tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
   trace.set_tracer_provider(tracer_provider)
   ```

4. **Weave SDK 초기화**
   ```python
   weave.init(PROJECT_ID)
   ```

## 📊 Weave 대시보드 사용

### 접속

1. https://wandb.ai 로그인
2. 프로젝트 선택 (예: `mason-choi-storika/WeaveHacks2`)
3. **Traces** 탭 클릭

### Timeline View

각 trace를 클릭하면 다음을 확인할 수 있습니다:

- **LLM Calls**: 모델 이름, 입력/출력, latency, cost
- **Tool Invocations**: 호출된 도구, 파라미터, 결과
- **Agent Flow**: 에이전트 간 데이터 전달 순서
- **Errors**: 실패한 작업의 stack trace

### 성능 분석

- **Latency**: 각 단계의 실행 시간
- **Cost**: LLM 호출 비용 추적
- **Token Usage**: 입력/출력 토큰 수
- **Success Rate**: 성공/실패 비율

## 🧪 테스트

### 기본 테스트

```bash
python examples/test_cmo_weave_otel.py
```

### 예상 출력

```
============================================================
🔍 환경 변수 확인
============================================================
   WANDB_API_KEY: ✅ 설정됨
   GOOGLE_API_KEY: ✅ 설정됨
   WANDB_PROJECT_ID: mason-choi-storika/WeaveHacks2

✅ 모든 필수 환경 변수가 설정되었습니다.

📡 Weave 프로젝트: mason-choi-storika/WeaveHacks2
   대시보드: https://wandb.ai/mason-choi-storika/WeaveHacks2

[INFO] 🐝 OpenTelemetry configured for Weave: mason-choi-storika/WeaveHacks2
[INFO] 🐝 Weave SDK initialized: mason-choi-storika/WeaveHacks2

============================================================
테스트: CMO Agent with OpenTelemetry Weave Integration
============================================================

📝 사용자 요청: 오늘의 트렌드를 기반으로 quote tweet을 만들어줘

⏳ CMO Agent 실행 중...
   - OpenTelemetry traces가 Weave로 전송됩니다
   - Weave 대시보드에서 실시간으로 확인 가능합니다

✅ CMO Agent 실행 완료!

============================================================
🐝 Weave 대시보드에서 traces를 확인하세요:
   URL: https://wandb.ai/mason-choi-storika/WeaveHacks2
   - Traces 탭 클릭
   - Timeline View에서 실행 흐름 분석
   - 각 LLM call과 tool invocation 확인
============================================================
```

## 🔧 트러블슈팅

### 에러: "WANDB_API_KEY not found"

**원인**: 환경 변수가 설정되지 않음

**해결**:
```bash
# .env 파일 생성
echo 'WANDB_API_KEY=your_key' >> .env
echo 'GOOGLE_API_KEY=your_key' >> .env

# 또는 export
export WANDB_API_KEY=your_key
export GOOGLE_API_KEY=your_key
```

### Traces가 Weave에 나타나지 않음

**원인**: 
1. API Key가 잘못됨
2. 프로젝트 ID가 잘못됨
3. 네트워크 연결 문제

**해결**:
1. API Key 확인: https://wandb.ai/authorize
2. 프로젝트 ID 형식 확인: `entity/project`
3. 네트워크 연결 확인
4. 로그 확인:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### ADK가 추적되지 않음

**원인**: Tracer Provider가 ADK import 후에 설정됨

**해결**: `cmo_agent.agent`를 import하면 자동으로 올바른 순서로 설정됩니다.

```python
# ✅ 올바른 순서 (자동 처리)
from cmo_agent.agent import root_agent

# ❌ 잘못된 순서
from google.adk.agents import LlmAgent  # ADK를 먼저 import하면 안됨
trace.set_tracer_provider(...)  # 너무 늦음
```

## 🎨 고급 사용법

### 커스텀 프로젝트 사용

```bash
export WANDB_PROJECT_ID=my-company/my-project
```

### Self-Hosted Weave

```python
# cmo_agent/agent.py 수정
WANDB_BASE_URL = "https://your-weave-host.com"
OTEL_EXPORTER_OTLP_ENDPOINT = f"{WANDB_BASE_URL}/traces/otel/v1/traces"
```

### 추가 Spans 추적

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@weave.op()
def my_custom_function():
    with tracer.start_as_current_span("custom_operation"):
        # your code here
        pass
```

## 📈 베스트 프랙티스

1. **환경 변수 보안**
   - `.env` 파일을 `.gitignore`에 추가
   - API Key를 코드에 직접 입력하지 않기
   - 프로덕션에서는 secrets manager 사용

2. **프로젝트 조직화**
   - 개발: `entity/project-dev`
   - 스테이징: `entity/project-staging`
   - 프로덕션: `entity/project-prod`

3. **성능 최적화**
   - Batch processing으로 여러 요청 묶기
   - Sampling rate 조정 (대량 트래픽 시)
   - Async exporter 사용 고려

## 🤝 도움말

- **Weave 문서**: https://weave-docs.wandb.ai
- **ADK 문서**: https://google.github.io/adk-docs
- **커뮤니티**: https://wandb.ai/site/community
- **GitHub Issues**: https://github.com/wandb/weave

---

**마지막 업데이트**: 2025-10-12  
**버전**: 1.0  
**참고**: [Weave ADK Integration Guide](https://weave-docs.wandb.ai/guides/integrations/google_adk/)

