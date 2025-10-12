# Using Content History & Trends with CMO Agent

이 디렉토리에는 이전 컨텐츠 성과 데이터와 트렌드 정보를 CMO Agent와 함께 사용하는 예제가 포함되어 있습니다.

## 📁 파일 구조

```
examples/
├── content_history_sample.json      # 샘플 컨텐츠 히스토리 & 트렌드 데이터
├── use_content_history.py          # 히스토리 데이터 분석 유틸리티
├── cmo_with_history.py             # CMO Agent + 히스토리 통합 예제
└── README_HISTORY_USAGE.md         # 이 파일
```

## 📊 Content History Sample 구조

`content_history_sample.json` 파일은 다음을 포함합니다:

### 1. **Content History** (이전 게시물)
```json
{
  "content_history": [
    {
      "id": "post_001",
      "date": "2025-10-05",
      "content": {...},
      "scores": {
        "novelty": 0.85,
        "creativity": 0.80,
        "overall": 0.81
      },
      "actual_performance": {
        "views": 15420,
        "engagement_rate": 0.078
      },
      "feedback": "High engagement from developer community..."
    }
  ]
}
```

### 2. **Performance Trends** (성과 분석)
```json
{
  "performance_trends": {
    "top_performing_characteristics": {
      "content_types": [...],
      "tone": {...},
      "best_hashtags": [...]
    },
    "audience_insights": {...},
    "recommendations": [...]
  }
}
```

### 3. **Current Trends** (현재 트렌드)
```json
{
  "current_trends": {
    "platform_trends": {
      "twitter": [...],
      "linkedin": [...]
    },
    "emerging_topics": [...]
  }
}
```

## 🚀 사용 방법

### 1. 히스토리 데이터 분석

```bash
cd examples
python use_content_history.py
```

**출력:**
- 최고 성과 게시물 Top 3
- 성과 패턴 분석
- Research Agent용 컨텍스트
- 주요 권장사항

### 2. CMO Agent와 함께 사용 (권장 방법)

```bash
python run_cmo_with_history_input.py
```

이 스크립트는:
1. 히스토리 데이터를 CMO Agent 입력으로 포맷팅
2. 실제 ADK 실행 방법 안내
3. 예상 워크플로우 설명

### 3. 실제 ADK로 실행

**Option A: 히스토리 데이터 포함 (권장)**

```python
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from cmo_agent.agent import root_agent
import json

# 히스토리 로드
with open("examples/content_history_sample.json") as f:
    history = json.load(f)

# ADK Runner 생성
runner = InMemoryRunner(root_agent, "cmo_agent")
session = runner.session_service().create_session("cmo_agent", "user_01").blockingGet()

# 히스토리 데이터와 함께 요청
message_text = f'''
Generate next content.

Historical data:
{json.dumps(history, indent=2)}
'''

message = Content.fromParts(Part.fromText(message_text))
events = runner.runAsync("user_01", session.id(), message)

# 결과 처리
for event in events.blockingIterable():
    if event.finalResponse():
        result = event.stringifyContent()
        content_result = json.loads(result)
        print(f"✅ Selected: {content_result['selected']['text']}")
        print(f"📊 Expected Score: {content_result['selected']['expected_overall']}")
```

**Option B: 간단하게 (히스토리 없이)**

```python
# 간단한 요청 - CMO Agent가 알아서 트렌드 조사
message = Content.fromParts(Part.fromText("Give me next content"))
events = runner.runAsync("user_01", session.id(), message)
```

## 📈 주요 인사이트 (샘플 데이터 기준)

### 최고 성과 컨텐츠 특성

1. **Behind-the-scenes** 컨텐츠
   - 평균 참여율: **9.2%**
   - 예시: "Plot twist: AI rejected our CEO's tweet"
   - 왜 효과적인가: 투명성 + 유머

2. **Provocative Future** 컨텐츠
   - 평균 참여율: **7.8%**
   - 예시: "We built an AI that hires other AIs"
   - 왜 효과적인가: 미래 비전 + 대담함

3. **Comparison** 컨텐츠
   - 평균 참여율: **6.1%**
   - 예시: "Traditional hiring vs AI hiring"
   - 왜 효과적인가: 명확한 대조

### 톤 분석

| 톤 | 평균 참여율 | 권장 사용 |
|---|---|---|
| Humorous | 9.2% | ✅ 높음 (authentic할 때) |
| Provocative | 7.6% | ✅ 중간 |
| Data-driven | 7.5% | ✅ 중간 |
| Professional | 6.1% | ⚠️ 낮음 (LinkedIn 제외) |

### 최적 포맷

- **Twitter**: 80-120자, 해시태그 2-3개
- **LinkedIn**: 150-200자, 전문적 톤
- **최고 해시태그**: #AI, #BuildInPublic, #FutureOfWork

### 청중 세그먼트

1. **AI/ML Engineers** (8.9% 참여율)
   - 관심사: 자율 시스템, 에이전트 아키텍처, 비하인드 스토리
   
2. **Tech Founders** (8.2% 참여율)
   - 관심사: 일의 미래, 자동화, 투명성

3. **Developer Community** (7.5% 참여율)
   - 관심사: 방법론, 기술 세부사항, 데이터 기반 접근

## 🎯 권장사항

샘플 데이터 분석 결과, 다음 컨텐츠에 대한 권장사항:

1. ✅ **Behind-the-scenes 컨텐츠 증가** - 가장 높은 참여율 (9.2%)
2. ✅ **진정성 있는 유머 사용** - 기술 청중에게 공감
3. ✅ **투명성과 취약성** - CEO 거절 스토리가 효과적
4. ✅ **짧고 강렬하게** - 80-120자가 더 긴 것보다 효과적
5. ✅ **데이터 기반 인사이트** - 기술 청중은 동기부여보다 인사이트 선호
6. ⚠️ **프로젝트명 과도한 홍보 피하기** - 가치/인사이트에 집중

## 🔄 워크플로우

```
1. Load History Data
   ↓
2. Analyze Performance Patterns
   ↓
3. Format Context for Research Agent
   ↓
4. CMO Agent Receives Enhanced Prompt
   ↓
5. Research Agent (with historical context)
   ↓
6. LoopAgent (10 iterations)
   - Creative Writer (learns from patterns)
   - Generator (applies best formats)
   - Critic (evaluates quality)
   ↓
7. Select Best Result
   ↓
8. Safety Validation
   ↓
9. Output with Performance Prediction
```

## 📝 자체 데이터 사용하기

실제 데이터를 사용하려면:

1. `content_history_sample.json`을 템플릿으로 복사
2. 실제 게시물 데이터로 교체:
   - 실제 성과 메트릭 (views, engagement_rate 등)
   - 실제 피드백 및 인사이트
3. 현재 트렌드 정보 업데이트
4. `use_content_history.py` 실행하여 분석

## 🧪 테스트

```bash
# 히스토리 분석 실행
python examples/use_content_history.py

# CMO 통합 예제 실행
python examples/cmo_with_history.py

# 실제 CMO Agent 실행 (ADK 필요)
adk run cmo_agent --input "AI agents topic with historical context"
```

## 📚 관련 문서

- [CMO Agent 가이드](../CMO_AGENT_SUMMARY.md)
- [Sequential Layers](../SEQUENTIAL_LAYERS_README.md)
- [Full System Guide](../FULL_SYSTEM_GUIDE.md)

## 💡 팁

1. **정기적으로 업데이트**: 새 게시물 발행 후 히스토리에 추가
2. **A/B 테스트**: 여러 variation 시도 후 결과 기록
3. **트렌드 추적**: 매주 current_trends 섹션 업데이트
4. **피드백 루프**: 실제 성과를 예측과 비교하여 개선

---

Made with ❤️ for WeaveHacks2

