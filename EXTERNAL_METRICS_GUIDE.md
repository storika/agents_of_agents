# 외부 메트릭 & 바이럴 상황 입력 가이드

## 📊 바이럴 콘텐츠 상황을 HR Agent에게 알리는 방법

### 1️⃣ 외부 메트릭 입력 구조

`team_state.json`에 실제 플랫폼 성과 데이터를 포함하세요:

```json
{
  "iteration": 5,
  "agents": [
    {
      "name": "ViralHook",
      "role": "writer.specialist",
      "utility": 0.88,
      "content_count": 3,
      "best_external_metrics": {
        "twitter_likes": 3200,
        "twitter_retweets": 580,
        "twitter_replies": 145,
        "linkedin_reactions": 890,
        "linkedin_shares": 234,
        "reddit_upvotes": 1500,
        "reddit_comments": 89,
        "views": 48000,
        "click_through_rate": 0.12
      },
      "last_scores": { ... }
    }
  ],
  "score_history": {
    "avg_overall": [0.65, 0.68, 0.72, 0.75, 0.79],
    "dims_mean": {
      "clarity": 0.83,
      "novelty": 0.67,
      "shareability": 0.74,
      "credibility": 0.78,
      "safety": 0.93
    },
    "external_metrics": [
      {
        "twitter_likes": 3200,
        "twitter_retweets": 580,
        "views": 48000,
        "click_through_rate": 0.12
      }
    ]
  }
}
```

### 2️⃣ 외부 메트릭 필드

#### Agent-level Metrics (`best_external_metrics`)
각 에이전트가 기여한 콘텐츠의 **최고 성과**를 기록:

| 필드 | 설명 | 예시 |
|------|------|------|
| `twitter_likes` | 트위터 좋아요 수 | 3200 |
| `twitter_retweets` | 트위터 리트윗 수 | 580 |
| `twitter_replies` | 트위터 답글 수 | 145 |
| `linkedin_reactions` | LinkedIn 반응 수 | 890 |
| `linkedin_shares` | LinkedIn 공유 수 | 234 |
| `reddit_upvotes` | Reddit 업보트 수 | 1500 |
| `reddit_comments` | Reddit 댓글 수 | 89 |
| `views` | 총 조회수/노출수 | 48000 |
| `click_through_rate` | 클릭률 (0-1) | 0.12 |

#### Team-level Metrics (`score_history.external_metrics`)
최근 콘텐츠의 **시간순 성과 기록** (최신순):

```json
"external_metrics": [
  {
    "twitter_likes": 3200,
    "twitter_retweets": 580,
    "views": 48000
  },
  {
    "twitter_likes": 1200,
    "twitter_retweets": 180,
    "views": 15000
  }
]
```

### 3️⃣ 평가 지표 (Evaluation Dimensions)

HR Agent는 **5가지 차원**으로 콘텐츠를 평가합니다:

#### Internal Scores (LLM 평가, 0-1)

| 차원 | 의미 | 예시 평가 기준 |
|------|------|---------------|
| `clarity` | 명확성 | 이해하기 쉬운가? 복잡한 개념을 잘 설명하는가? |
| `novelty` | 신선함 | 새로운 관점인가? 예상치 못한 인사이트가 있나? |
| `shareability` | 공유 가능성 | 친구에게 공유하고 싶은가? 감정적 공감이 있나? |
| `credibility` | 신뢰성 | 근거가 충분한가? 정확한가? 출처가 명확한가? |
| `safety` | 안전성 | 윤리적인가? 편견이 없나? 해롭지 않나? |

#### External Metrics (실제 플랫폼 데이터)

자동 계산되는 지표:

```python
# Engagement Rate
engagement_rate = (likes + retweets + replies + shares) / views

# Viral Score (공유율 기반, 0-1)
viral_score = min(1.0, (retweets + shares) / views * 20)
# → 5% 이상 공유되면 1.0 (완전 바이럴)
```

### 4️⃣ 바이럴 상황 예시

#### 🔥 바이럴 성공 (ViralHook 에이전트)

```json
{
  "name": "ViralHook",
  "utility": 0.88,
  "best_external_metrics": {
    "views": 48000,
    "twitter_likes": 3200,
    "twitter_retweets": 580,
    "engagement_rate_calculated": 0.097  // 9.7%
  },
  "last_scores": {
    "shareability": 0.92,  // 높음!
    "novelty": 0.80,       // 높음!
    "clarity": 0.75
  }
}
```

**HR Agent의 판단:**
- ✅ Utility 높음 (0.88) → 유지
- ✅ 외부 성과 우수 → 이 에이전트 스타일 확대

#### 😐 평범한 성과 (Explainer 에이전트)

```json
{
  "name": "Explainer",
  "utility": 0.72,
  "best_external_metrics": {
    "views": 1200,
    "twitter_likes": 45,
    "twitter_retweets": 8,
    "engagement_rate_calculated": 0.044  // 4.4%
  },
  "last_scores": {
    "clarity": 0.85,       // 높음
    "shareability": 0.60,  // 낮음
    "novelty": 0.55        // 낮음
  }
}
```

**HR Agent의 판단:**
- ⚠️ Utility 보통 (0.72) → 코칭 고려
- ⚠️ 외부 성과 낮음 → novelty/shareability 개선 필요
- 💡 프롬프트 피드백: "더 신선한 각도와 감정적 공감 추가"

### 5️⃣ HR Agent의 LLM 기반 결정

#### 초기 팀 생성 시
```json
{
  "project_goal": "Create viral social media content",
  "target_audience": "Young adults (18-35) on Twitter/LinkedIn",
  "content_focus": "Tech trends, productivity, career advice"
}
```

→ LLM이 **바이럴에 최적화된 초기 팀** 제안:
- IdeaGenerator (창의적 아이디어)
- Hooksmith (매력적인 오프닝)
- ShareabilityCritic (바이럴 잠재력 평가)

#### 성과 개선 채용 시
```
[INFO] Team weakness detected: novelty=0.52
[INFO] Current team: Explainer (writer), EngageCritic (critic)
[INFO] Using LLM to design specialist...
```

→ LLM이 현재 팀 분석 후 **맞춤 전문가** 설계:
```json
{
  "name": "TrendSpotter",
  "role": "writer.specialist",
  "system_prompt": "You are TrendSpotter, expert in viral trends...",
  "reason": "Improve novelty by identifying emerging topics"
}
```

### 6️⃣ 실전 워크플로우

1. **콘텐츠 생성** (Writers)
2. **LLM 평가** (Critics) → `last_scores` 업데이트
3. **외부 배포** (Twitter, LinkedIn, Reddit)
4. **메트릭 수집** (24-48시간 후)
5. **team_state 업데이트**:
   - `best_external_metrics`: 각 에이전트의 최고 성과
   - `external_metrics`: 최근 콘텐츠 시계열
6. **HR Agent 실행** → 팀 최적화 결정
7. **결정 적용** (채용/제거/코칭)
8. **반복**

### 7️⃣ 예시: 완전한 Input

```bash
# examples/team_viral_context.json 참고
uv run python -c "
from hr_validation_agent.agent import analyze_team_and_decide
import json

with open('examples/team_viral_context.json') as f:
    result = analyze_team_and_decide(json.dumps(json.load(f)))
    
print(json.loads(result)['hire_plan'])
"
```

## 🎯 핵심 포인트

1. **External Metrics**는 **선택사항** (없으면 internal scores만 사용)
2. **LLM이 자동으로 팀 구성 최적화** (초기 팀 + 전문가 채용)
3. **바이럴 성과**는 `shareability` + `engagement_rate` 조합
4. **실패 학습**: `failures` 필드에 이전 실패 이유 추가
5. **반복 개선**: 매 iteration마다 외부 성과 피드백

---

**버전**: 0.5.0  
**업데이트**: 2025-10-11

