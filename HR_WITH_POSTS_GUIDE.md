# HR Validation with Recent Posts - 간편 사용 가이드

## 🎯 개요

이제 **최근 post 데이터만** 넘기면 자동으로 현재 CMO agent의 프롬프트를 읽어와서 HR validation을 실행할 수 있습니다!

### 이전 vs 현재

**이전 방식** ❌:
```json
{
  "iteration": 1,
  "layers": {
    "research": {
      "current_version": 1,
      "metrics": {...},
      "prompt_history": [{
        "version": 1,
        "prompt": "완전한 프롬프트 텍스트를 여기에 복붙...",  // 😫
        ...
      }]
    },
    // 5개 레이어 전부 반복...
  }
}
```
- 모든 레이어의 프롬프트를 수동으로 복사 붙여넣기
- 수백 줄의 JSON 작성 필요
- 번거롭고 오류 발생 가능

**현재 방식** ✅:
```python
recent_posts = [
    {
        "content_id": "post_123",
        "internal_scores": {"clarity": 0.75, "novelty": 0.68, ...},
        "actual_performance": {"impressions": 5000, "likes": 120, ...}
    }
]

run_hr_with_recent_posts(recent_posts, iteration=1)  # 끝!
```
- 최근 post 성능 데이터만 제공
- 프롬프트는 `cmo_agent/sub_agents.py`에서 자동 읽기
- 간편하고 빠름!

---

## 🚀 빠른 시작

### 1. 최근 Post 데이터 준비

```python
recent_posts = [
    {
        "content_id": "post_001",
        "contributors": ["research", "creative_writer", "generator"],
        "internal_scores": {
            "clarity": 0.78,
            "novelty": 0.72,
            "shareability": 0.48,
            "credibility": 0.80,
            "safety": 0.95
        },
        "actual_performance": {
            "impressions": 5000,
            "likes": 120,
            "retweets": 18,
            "replies": 5,
            "engagement_rate": 0.029
        }
    },
    # ... more posts
]
```

### 2. 실행

```bash
python run_hr_with_posts.py
```

또는 코드에서:

```python
from run_hr_with_posts import run_sync

run_sync(recent_posts, iteration=1)
```

---

## 📊 Post 데이터 형식

### 필수 필드

```python
{
    "content_id": str,          # 고유 ID
    "contributors": [str],      # 참여한 레이어들
    "internal_scores": {        # 내부 평가 점수
        "clarity": float,       # 0-1
        "novelty": float,
        "shareability": float,
        "credibility": float,
        "safety": float
    },
    "actual_performance": {     # 실제 성과 (optional)
        "impressions": int,
        "likes": int,
        "retweets": int,
        "replies": int,
        "engagement_rate": float
    }
}
```

### 실제 예시

```python
{
    "content_id": "post_20251012_001",
    "contributors": ["research", "creative_writer", "generator"],
    "internal_scores": {
        "clarity": 0.78,
        "novelty": 0.72,
        "shareability": 0.48,
        "credibility": 0.80,
        "safety": 0.95
    },
    "actual_performance": {
        "impressions": 5000,
        "likes": 120,
        "retweets": 18,
        "replies": 5,
        "engagement_rate": 0.029  # (120+18+5)/5000
    }
}
```

---

## 🛠️ 새로운 Tools

### 1. `load_current_cmo_prompts()`

현재 CMO agent의 모든 프롬프트를 자동으로 읽어옵니다.

```python
from hr_validation_agent.tools_prompt_loader import load_current_cmo_prompts

prompts_json = load_current_cmo_prompts()
data = json.loads(prompts_json)

# 결과:
{
    "iteration": 0,
    "layers": {
        "research": {
            "current_version": 1,
            "metrics": {...},  # 기본값
            "prompt_history": [{
                "version": 1,
                "prompt": "실제 프롬프트 from sub_agents.py",
                "is_active": True
            }]
        },
        # ... 모든 레이어
    },
    "thresholds": {...}
}
```

### 2. `create_hr_input_from_posts()`

Post 데이터 + 현재 프롬프트 → 완전한 HR input 생성

```python
from hr_validation_agent.tools_prompt_loader import create_hr_input_from_posts

hr_input = create_hr_input_from_posts(
    json.dumps(recent_posts),
    iteration=1
)

# 결과: 완전한 HR validation input JSON
```

---

## 📁 출력 파일

### 자동 생성되는 파일들

1. **`hr_input_iteration_N_from_posts.json`**
   - 생성된 완전한 HR input
   - 디버깅 및 검증용

2. **`hr_results_iteration_N_from_posts.json`**
   - HR agent의 분석 결과
   - 개선 제안 포함

---

## 🔄 워크플로우

```
┌─────────────────────────────────────────────┐
│  1. Recent Posts (최근 성과 데이터)        │
│     - 3~10개 post 권장                      │
│     - Internal scores + Actual performance  │
└─────────────┬───────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────┐
│  2. Load Current Prompts                    │
│     - cmo_agent/sub_agents.py 자동 읽기    │
│     - 모든 레이어 프롬프트 추출             │
└─────────────┬───────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────┐
│  3. Create HR Input                         │
│     - Posts + Prompts → Complete JSON       │
│     - Aggregate metrics 계산                │
└─────────────┬───────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────┐
│  4. Run HR Sequential Agent                 │
│     - Analyzer → Evaluator → Improver       │
│     - 자동 분석 및 개선안 생성              │
└─────────────┬───────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────┐
│  5. Auto-Apply Improvements                 │
│     - apply_prompt_improvements 자동 호출   │
│     - sub_agents.py 업데이트               │
│     - Backup 생성 (cmo_agent_vN)           │
└─────────────────────────────────────────────┘
```

---

## 💡 사용 팁

### Tip 1: 적정 Post 개수

```python
# ❌ 너무 적음
recent_posts = [post1]  # 1개 - 통계적으로 의미 없음

# ✅ 적정
recent_posts = [post1, post2, post3, post4, post5]  # 3~10개 권장

# ⚠️ 너무 많음
recent_posts = [...]  # 50개+ - 너무 많은 데이터, 느림
```

### Tip 2: Iteration 관리

```python
# Iteration 0: Bootstrap (initial prompts)
run_sync(initial_posts, iteration=0)

# Iteration 1: First improvement
run_sync(posts_after_v1, iteration=1)

# Iteration 2: Second improvement
run_sync(posts_after_v2, iteration=2)
```

### Tip 3: 실제 성과 데이터가 없을 때

```python
# actual_performance를 생략 가능
post = {
    "content_id": "post_001",
    "contributors": ["research", "creative_writer"],
    "internal_scores": {
        "clarity": 0.78,
        "novelty": 0.72,
        # ...
    }
    # actual_performance 생략 - internal scores만으로 분석
}
```

### Tip 4: 빠른 프롬프트 확인

```python
# 현재 프롬프트만 보고 싶을 때
from hr_validation_agent.tools_prompt_loader import load_current_cmo_prompts
import json

prompts = json.loads(load_current_cmo_prompts())
print(prompts['layers']['research']['prompt_history'][0]['prompt'])
```

---

## 🔧 문제 해결

### Q: "sub_agents.py not found" 에러

**A:** 경로 확인
```bash
ls -la cmo_agent/sub_agents.py
```

### Q: JSON 파싱 에러

**A:** Post 데이터 형식 확인
```python
# 모든 필드가 올바른 타입인지 확인
post = {
    "content_id": "string",  # str ✅
    "contributors": ["research"],  # list[str] ✅
    "internal_scores": {"clarity": 0.78},  # dict[str, float] ✅
    "actual_performance": {"impressions": 5000}  # dict[str, int/float] ✅
}
```

### Q: 프롬프트가 업데이트 안됨

**A:** apply_prompt_improvements 확인
```python
# improver_agent가 자동으로 호출해야 함
# 로그에서 "✅ [Tool] CMO Agent 업데이트 시작..." 확인
```

---

## 📚 관련 문서

- [CMO_VERSION_UPDATER_GUIDE.md](./CMO_VERSION_UPDATER_GUIDE.md) - 버전 관리 상세
- [CMO_AGENT_VERSION_HISTORY.md](./CMO_AGENT_VERSION_HISTORY.md) - 버전별 변경 이력
- [hr_validation_agent/agent.py](./hr_validation_agent/agent.py) - Agent 구현

---

## 🎉 장점 요약

1. ✅ **간편성**: Post 데이터만 준비하면 됨
2. ✅ **자동화**: 프롬프트 읽기, 분석, 적용 모두 자동
3. ✅ **안전성**: 자동 백업 생성
4. ✅ **추적성**: 모든 변경사항 기록
5. ✅ **확장성**: 새 레이어 추가 쉬움

**이제 post 성과만 모니터링하면 자동으로 프롬프트가 개선됩니다!** 🚀

