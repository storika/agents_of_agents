# Image Caption Agent

트위터용 이미지와 캡션을 생성하는 오케스트레이터 에이전트입니다.

## 개요

이 에이전트는 주어진 주제(topic)를 바탕으로:

1. **3:4 비율의 세로형 이미지** (896×1280, Base64 인코딩)
2. **트위터 캡션** (≤280자, 이모지 허용)
3. **ALT 텍스트** (80-120자, 접근성)
4. **Safety 점수** (0-1, 콘텐츠 안전성 평가)

를 자동으로 생성합니다.

## 기능

### 1. 이미지 생성

- **모델**: Imagen 3.0 (Google Vertex AI)
- **비율**: 3:4 세로형 (896×1280)
- **품질**: 소셜 미디어 최적화
- **재시도**: 실패 시 자동 1회 재시도

### 2. 캡션 생성

- **길이**: 최대 280자 (목표 270자)
- **이모지**: 허용 (1-3개 권장)
- **해시태그**: 사용자 지정 개수 (기본 2개)
- **다국어**: locale 파라미터로 언어 지정
- **톤**: friendly, witty, informative, minimal

### 3. ALT 텍스트

- **길이**: 80-120자
- **내용**: 사실 기반 이미지 설명
- **목적**: 시각 장애인 접근성

### 4. Safety 점수

- **범위**: 0.0 (위험) ~ 1.0 (안전)
- **기준**:
  - 금지 키워드 매칭
  - 혐오/폭력/정치 선동 감지
  - 의료/금융 허위 주장 체크
  - 스팸성 콘텐츠 감지
- **권장**: score ≥ 0.7 이상일 때 게시

## 사용법

### 입력 스키마

```python
from image_caption_agent.schemas import ImageCaptionInput

input_data = ImageCaptionInput(
    topic="AI와 창의성의 만남",
    tone="friendly",  # optional: friendly, witty, informative, minimal
    locale="ko",  # optional: en, ko, ja, es, fr 등
    hashtagsAllowed=2,  # optional: 0-5
    safetyBans=["폭력", "혐오"]  # optional: 금지 키워드 리스트
)
```

### 출력 스키마

```python
{
    "imageBase64": "iVBORw0KGgoAAAANSUhEUgAA...",  # Base64 인코딩된 이미지
    "caption": "AI와 인간의 창의성이 만나면 무슨 일이 일어날까요? 🎨✨ 기술은 우리의 상상력을 확장하고, 예술은 기술에 영혼을 불어넣습니다. 당신은 어떤 분야에서 AI를 활용하고 싶나요? #AI #창의성",
    "altText": "밝은 색상의 추상적인 디지털 아트. 파란색과 주황색 빛이 어우러진 기하학적 패턴. 중앙에 빛나는 원형 오브젝트.",
    "safety": {
        "score": 0.95,
        "reasons": []  # 감점 사유 없음
    }
}
```

### 기본 사용 예시

```python
import asyncio
from image_caption_agent.agent import generate_image_caption_content
from image_caption_agent.schemas import ImageCaptionInput

async def main():
    # 입력 데이터 준비
    input_data = ImageCaptionInput(
        topic="커피와 아침의 여유",
        tone="friendly",
        locale="ko",
        hashtagsAllowed=2
    )

    # 콘텐츠 생성
    output = await generate_image_caption_content(input_data)

    # 결과 확인
    print(f"캡션: {output.caption}")
    print(f"ALT 텍스트: {output.altText}")
    print(f"안전 점수: {output.safety.score}")

    if output.safety.score >= 0.7:
        print("✅ 게시에 적합한 콘텐츠입니다.")
    else:
        print("⚠️ 안전 점수가 낮습니다:")
        for reason in output.safety.reasons:
            print(f"  - {reason}")

if __name__ == "__main__":
    asyncio.run(main())
```

### ADK Agent 직접 사용

```python
from image_caption_agent.agent import orchestrator_agent

# 에이전트 실행
response = await orchestrator_agent.run("""
주제: 우주 탐사의 미래
톤: informative
언어: en
해시태그: 3개
""")
```

## 입력 파라미터 상세

| 파라미터          | 타입     | 필수 | 기본값     | 설명                                            |
| ----------------- | -------- | ---- | ---------- | ----------------------------------------------- |
| `topic`           | string   | ✅   | -          | 이미지와 캡션의 주제                            |
| `tone`            | string   | ❌   | "friendly" | 캡션 톤 (friendly, witty, informative, minimal) |
| `locale`          | string   | ❌   | "en"       | 언어 코드 (en, ko, ja, es, fr 등)               |
| `hashtagsAllowed` | number   | ❌   | 2          | 허용되는 최대 해시태그 개수 (0-5)               |
| `safetyBans`      | string[] | ❌   | null       | 금지 키워드 리스트                              |

## 출력 필드 상세

| 필드             | 타입     | 설명                                                |
| ---------------- | -------- | --------------------------------------------------- |
| `imageBase64`    | string   | Base64로 인코딩된 PNG 이미지 (3:4 세로형, 896×1280) |
| `caption`        | string   | 트위터 캡션 (≤280자, 이모지 포함)                   |
| `altText`        | string   | ALT 텍스트 (80-120자, 이미지 설명)                  |
| `safety.score`   | float    | 안전 점수 (0.0-1.0)                                 |
| `safety.reasons` | string[] | 감점 사유 리스트 (없으면 빈 배열)                   |

## 캡션 작성 규칙

1. **첫 문장 훅**: 질문, 수치, 대조 중 하나 선택
2. **감정/가치**: 재치, 공감, 놀라움 중 하나 표현
3. **시의성** (선택): 트렌드나 타이밍 언급
4. **마무리**: 댓글 유도형 질문 또는 미세 CTA

### 금지 사항

- ❌ 클릭베이트/과장
- ❌ 혐오/차별/폭력/정치 선동
- ❌ 의료/금융 허위 주장
- ❌ 상표/저작권 남용
- ❌ 과도한 이모지/해시태그 (스팸성)

## Safety 점수 산정

시작 점수 **1.0**에서 다음과 같이 감점:

| 위반 항목               | 감점  | 설명                                   |
| ----------------------- | ----- | -------------------------------------- |
| 금지 키워드 매칭 (중대) | -0.4  | safetyBans에 명시된 긴 키워드 (>4자)   |
| 금지 키워드 매칭 (경미) | -0.2  | safetyBans에 명시된 짧은 키워드 (≤4자) |
| 혐오/폭력/정치 선동     | -0.5  | 유해 콘텐츠 패턴 감지                  |
| 의료/금융 허위 주장     | -0.5  | 전문적 주장 패턴 감지                  |
| 과도한 상업/과장        | -0.15 | 클릭베이트, 과장 광고                  |
| 스팸성 해시태그 (>5개)  | -0.2  | 과도한 해시태그 사용                   |
| 스팸성 이모지 (>5개)    | -0.1  | 과도한 이모지 사용                     |

**권장 기준**: `score ≥ 0.7` → 게시 적합

## 예시

### 예시 1: 기술 주제 (영어)

```python
input_data = ImageCaptionInput(
    topic="quantum computing breakthrough",
    tone="informative",
    locale="en",
    hashtagsAllowed=3
)
```

**출력 예상**:

```
caption: "Quantum computers just achieved a major milestone 🚀 They can now solve problems in minutes that would take classical computers thousands of years. The future of computing is here. What would you solve with this power? #QuantumComputing #Tech #Future"

altText: "Abstract visualization of quantum computing. Glowing blue and purple spheres connected by light streams against dark background. Futuristic and technological atmosphere."

safety: { score: 0.95, reasons: [] }
```

### 예시 2: 라이프스타일 주제 (한국어)

```python
input_data = ImageCaptionInput(
    topic="건강한 아침 루틴",
    tone="friendly",
    locale="ko",
    hashtagsAllowed=2
)
```

**출력 예상**:

```
caption: "아침 30분이 하루를 바꿉니다 ☀️ 스트레칭, 명상, 건강한 아침식사. 작은 습관이 큰 변화를 만들어요. 당신의 아침 루틴은 무엇인가요? #아침루틴 #건강한습관"

altText: "밝은 햇살이 비치는 창가. 요가 매트 위에서 스트레칭하는 모습. 따뜻한 차와 과일이 놓인 테이블. 평화롭고 건강한 아침 분위기."

safety: { score: 1.0, reasons: [] }
```

### 예시 3: Safety 경고 케이스

```python
input_data = ImageCaptionInput(
    topic="revolutionary weight loss",
    tone="witty",
    locale="en",
    hashtagsAllowed=5,
    safetyBans=["miracle", "guaranteed"]
)
```

**출력 예상**:

```
safety: {
    score: 0.5,
    reasons: [
        "금지 키워드 'miracle' 중대 매칭",
        "금지 키워드 'guaranteed' 중대 매칭",
        "부적절한 콘텐츠: 의학적 주장"
    ]
}
⚠️ score < 0.7 → 게시 부적합
```

## 아키텍처

```
image_caption_agent/
├── __init__.py          # 패키지 초기화
├── agent.py             # 오케스트레이터 에이전트
├── schemas.py           # Pydantic 스키마 (입력/출력)
├── tools.py             # 도구 함수들
│   ├── generate_image_concept()
│   ├── generate_twitter_image()
│   ├── generate_twitter_caption()
│   ├── generate_alt_text()
│   └── calculate_safety_score()
└── README.md            # 이 문서
```

## 의존성

- `google-adk[ui]>=1.16.0` - Google ADK 프레임워크
- `google-generativeai>=0.8.5` - Gemini 및 Imagen API
- `pydantic>=2.0` - 스키마 검증
- `python>=3.11` - Python 버전

## 제한사항

1. **이미지 생성**:

   - Vertex AI 인증 필요
   - Imagen 3.0 모델 사용
   - 생성 실패 시 1회 재시도 후 진행

2. **캡션**:

   - 트위터 280자 제한 준수
   - 이모지는 문자 수에 포함
   - 해시태그는 사용자 지정 제한

3. **Safety**:
   - 규칙 기반 휴리스틱 (ML 모델 아님)
   - 100% 정확도 보장 불가
   - 최종 검토는 사람이 수행 권장

## 라이선스

Apache License 2.0

## 기여

이슈나 PR은 언제든 환영합니다!
