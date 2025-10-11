# CMO Agent - Sequential Layers

5개의 서브에이전트 레이어를 순차적으로 실행하여 콘텐츠를 생성, 평가, 발행하는 시스템입니다.

## 📋 구성

### 1. Research Layer
- **역할**: 트렌딩 토픽 조사, 청중 분석, 바이럴 각도 제안
- **출력**: 트렌딩 토픽, 청중 인사이트, 바이럴 각도, 데이터 소스

### 2. Creative Writer Layer
- **역할**: 창의적인 콘텐츠 아이디어 생성
- **출력**: 여러 콘텐츠 아이디어 (제목, hook, 각도, 플랫폼, 점수)

### 3. Generator Layer
- **역할**: 아이디어를 실제 공유 가능한 콘텐츠로 변환
- **출력**: 플랫폼별 콘텐츠 조각 (텍스트, 해시태그, CTA 등)

### 4. Critic Layer
- **역할**: 콘텐츠 품질 평가 (정확성, 객관성, 완성도)
- **출력**: 평가 점수 및 피드백

### 5. Safety Layer
- **역할**: 브랜드 안전성, 윤리, 법적 준수 검증
- **출력**: 안전성 점수, 위험 수준, 준수 상태, 위험 플래그

## 🚀 사용 방법

### 기본 실행

```bash
python test_sequential_layers.py
```

### 커스텀 주제로 실행

```bash
python test_sequential_layers.py "your custom topic here"
```

## 📊 임계값 (Thresholds)

콘텐츠가 승인되기 위해서는 다음 임계값을 충족해야 합니다:

- **clarity**: 0.55 (명확성)
- **novelty**: 0.55 (참신성)
- **shareability**: 0.55 (공유 가능성)
- **credibility**: 0.60 (신뢰도)
- **safety**: 0.80 (안전성)

## 🔄 실행 흐름

```
1. Research Layer
   ↓ (트렌딩 토픽, 청중 인사이트)
2. Creative Writer Layer
   ↓ (여러 아이디어 생성 → 최고 점수 선택)
3. Generator Layer
   ↓ (선택된 아이디어 → 실제 콘텐츠 생성)
4. Critic Layer
   ↓ (콘텐츠 품질 평가)
5. Safety Layer
   ↓ (안전성 검증)
최종 결정 (승인/거부/개선 필요)
```

## 📝 결과 상태

- **approved**: 모든 기준을 통과하여 승인됨
- **rejected**: 안전성 또는 준수 기준 미달로 거부됨
- **needs_improvement**: 품질 기준 미달로 개선 필요

## 📄 출력 파일

실행 결과는 `sequential_layers_result.json` 파일에 저장됩니다.

## 🛠️ 구현 파일

- **schemas.py**: 각 레이어의 입출력 스키마 정의
- **sub_agents.py**: 5개 레이어 에이전트 생성 및 호출 함수
- **agent.py**: `orchestrate_sequential_layers()` 오케스트레이션 함수
- **test_sequential_layers.py**: 테스트 실행 스크립트

## 💡 예제

```python
from cmo_agent.agent import orchestrate_sequential_layers

result_json = orchestrate_sequential_layers(
    topic="AI agents that hire other AI agents",
    audience_demographics="developers, tech enthusiasts"
)

import json
result = json.loads(result_json)
print(f"Status: {result['status']}")

# 임계값은 함수 내부에서 기본값으로 설정됩니다
# clarity=0.55, novelty=0.55, shareability=0.55, credibility=0.60, safety=0.80
```

## 🎯 특징

- ✅ 5개 레이어 순차적 실행
- ✅ 각 레이어의 구조화된 JSON 입출력
- ✅ 자동 품질 및 안전성 검증
- ✅ 상세한 실행 로그 출력
- ✅ Weave 통합으로 추적 가능
- ✅ 커스터마이징 가능한 임계값

## 📌 참고

- 각 레이어는 Gemini 2.5 Flash 모델을 사용합니다
- JSON 파싱 실패 시 기본값(fallback)을 사용합니다
- 모든 실행은 Weave에 자동으로 로깅됩니다

