# HR Validation Agent 사용 가이드

## 📋 개요

HR Validation Agent는 5-layer 콘텐츠 생성 시스템의 프롬프트를 자동으로 최적화하는 메타 에이전트입니다. 실제 콘텐츠 성과 데이터를 분석하여 각 레이어의 프롬프트를 개선합니다.

## 🏗️ 시스템 구조

### 5개 고정 레이어
1. **Research** - 트렌드 분석, 청중 이해, 바이럴 기회 식별
2. **Creative Writer** - 창의적 아이디어 생성, 신선한 각도 개발
3. **Generator** - 구체적 콘텐츠 생성 (트윗, 포스트)
4. **Critic** - 품질 평가 (clarity, novelty, shareability, credibility)
5. **Safety** - 브랜드 안전성, 윤리, 법적 기준 확인

### 핵심 기능
- ✅ **프롬프트 히스토리 추적** - 모든 프롬프트 버전 기록
- ✅ **실제 성과 분석** - impressions, likes, retweets 등 실제 메트릭 활용
- ✅ **버전별 효과 측정** - 어떤 프롬프트 버전이 효과적이었는지 분석
- ✅ **완전한 프롬프트 제공** - 수정사항이 아닌 완전한 새 프롬프트 출력
- ✅ **인사이트 자동 생성** - 패턴 인식 및 개선 방향 제시

## 📊 입력 데이터 구조

### `hr_input_with_actual_performance.json`

```json
{
  "iteration": 1,
  
  "layers": {
    "research": {
      "current_version": 1,
      "metrics": {
        "relevance": 0.65,
        "timeliness": 0.58,
        "data_quality": 0.70
      },
      "prompt_history": [
        {
          "version": 1,
          "prompt": "완전한 프롬프트 텍스트...",
          "created_at": "2025-10-12T00:00:00Z",
          "reason": "Initial prompt - bootstrap",
          "is_active": true
        }
      ]
    },
    "creative_writer": { ... },
    "generator": { ... },
    "critic": { ... },
    "safety": { ... }
  },
  
  "overall_metrics": {
    "clarity": 0.78,
    "novelty": 0.72,
    "shareability": 0.48,  // ⚠️ 낮음!
    "credibility": 0.85,
    "safety": 0.92,
    "overall": 0.68
  },
  
  "content_history": [
    {
      "content_id": "tweet_001",
      "text": "실제 트윗 텍스트...",
      "media_prompt": "이미지 생성 프롬프트...",
      "hashtags": ["#AIAgents", "#BuildInPublic"],
      "platform": "X",
      "character_count": 179,
      
      "contributors": ["research", "creative_writer", "generator"],
      
      "prompt_versions": {
        "research": 1,
        "creative_writer": 1,
        "generator": 1,
        "critic": 1,
        "safety": 1
      },
      
      "internal_scores": {
        "clarity": 0.85,
        "novelty": 0.78,
        "shareability": 0.72,
        "credibility": 0.82,
        "safety": 0.95
      },
      
      "actual_performance": {
        "impressions": 4,
        "views": 4,
        "likes": 0,
        "retweets": 0,
        "replies": 0,
        "bookmarks": 0,
        "engagement_rate": 0.0
      }
    }
    // ... 더 많은 콘텐츠
  ]
}
```

## 🔧 사용 방법

### 1. 기본 실행

```python
from hr_validation_agent.agent import root_agent
import json

# 데이터 로드
with open("hr_input_with_actual_performance.json") as f:
    data = json.load(f)

# Agent 실행
response = root_agent.execute(json.dumps(data))
result = json.loads(response)

# 프롬프트 업데이트 적용
for prompt_update in result["prompts"]:
    layer = prompt_update["layer"]
    new_prompt = prompt_update["new_prompt"]
    
    print(f"\n{'='*60}")
    print(f"📝 {layer} 레이어 업데이트")
    print(f"{'='*60}")
    print(f"이유: {prompt_update['reason']}")
    print(f"예상 효과: {prompt_update['expected_impact']}")
    print(f"\n새 프롬프트 (앞 200자):")
    print(new_prompt[:200] + "...")
    
    # 실제 시스템에 적용
    update_layer_prompt(layer, new_prompt)
```

### 2. Engagement 분석 도구 사용

```python
from hr_validation_agent.agent import evaluate_content_engagement
import json

# 데이터 준비
with open("hr_input_with_actual_performance.json") as f:
    data = json.load(f)

engagement_input = {
    "prompt_history": data["prompt_history"],
    "layers": data["layers"],
    "contents": data["content_history"]
}

# 분석 실행
analysis_json = evaluate_content_engagement(json.dumps(engagement_input))
analysis = json.loads(analysis_json)

# 결과 확인
print(f"📊 Engagement 분석 결과")
print(f"- 평균 engagement rate: {analysis['engagement_stats']['avg_engagement_rate']:.4f}")
print(f"- 고성과 콘텐츠: {analysis['engagement_stats']['high_performers_count']}개")
print(f"- 저성과 콘텐츠: {analysis['engagement_stats']['low_performers_count']}개")

# 프롬프트 버전별 효과
print(f"\n🔍 프롬프트 버전 효과:")
for prompt_key, perf in analysis["prompt_version_effectiveness"].items():
    total = perf["high"] + perf["low"]
    success_rate = perf["high"] / total if total > 0 else 0
    print(f"  {prompt_key}: {perf['high']}/{total} 성공 ({success_rate:.1%})")

# 인사이트
print(f"\n💡 인사이트:")
for insight in analysis["insights"]:
    print(f"\n  [{insight['type']}]")
    print(f"  메시지: {insight['message']}")
    print(f"  권장사항: {insight['recommendation']}")
```

## 📤 출력 형식

```json
{
  "prompts": [
    {
      "layer": "creative_writer",
      "new_prompt": "You are the Creative Writer layer...\n\n[완전한 새 프롬프트]",
      "reason": "shareability 0.48 < 0.55; novelty 0.72 borderline; actual engagement 0%",
      "expected_impact": "increase shareability by 0.15+ through stronger hooks; boost engagement to 2-5%"
    },
    {
      "layer": "generator",
      "new_prompt": "You are the Generator layer...\n\n[완전한 새 프롬프트]",
      "reason": "shareability 0.48 < threshold; 0% engagement despite good clarity",
      "expected_impact": "improve call-to-action strength and viral mechanics"
    }
  ],
  "global_adjustments": {
    "target_audience_update": null,
    "brand_voice": null,
    "topics_to_avoid": []
  },
  "thresholds": {
    "clarity_min": 0.55,
    "novelty_min": 0.55,
    "shareability_min": 0.55,
    "credibility_min": 0.60,
    "safety_min": 0.80
  }
}
```

## 🔄 워크플로우

### 1. 초기 설정 (Iteration 0)
```
1. 빈 prompt_history로 시작
2. HR Agent 실행 → 5개 레이어 모두 초기 프롬프트 생성
3. 각 layers[layer].prompt_history에 version 1 추가 (is_active=true)
4. 콘텐츠 생성 시작
```

### 2. 개선 루프 (Iteration 1+)
```
1. 콘텐츠 생성 및 배포
2. 실제 성과 수집 (24-48시간 후)
   - impressions, likes, retweets, replies, bookmarks
3. content_history 업데이트
   - actual_performance 입력
   - prompt_versions 기록
4. HR Agent 실행
   - evaluate_content_engagement로 패턴 분석
   - 문제 레이어 식별
   - 새 프롬프트 생성 (1-3개 레이어)
5. 새 프롬프트 적용
   - 기존 버전의 is_active를 false로 변경
   - prompt_history에 새 버전 추가 (is_active=true)
   - current_version 업데이트
6. 반복
```

## 📈 성과 측정

### Internal Scores (LLM 평가)
- **clarity**: 명확성 (0-1)
- **novelty**: 신선함 (0-1)
- **shareability**: 공유 가능성 (0-1)
- **credibility**: 신뢰성 (0-1)
- **safety**: 안전성 (0-1)

### External Metrics (실제 성과)
- **impressions**: 노출 횟수
- **likes**: 좋아요
- **retweets**: 리트윗
- **replies**: 답글
- **bookmarks**: 북마크
- **engagement_rate**: (likes + retweets + replies + bookmarks) / impressions

### 자동 계산 지표
- **avg_engagement_rate**: 평균 engagement rate
- **avg_viral_score**: 바이럴 점수 (리트윗 비율 기반)
- **prompt_version_effectiveness**: 버전별 성공률

## 🎯 최적화 전략

### 문제 상황별 대응

**1. Engagement 0% (현재 상황)**
```
문제: impressions는 있지만 아무도 반응하지 않음
원인: shareability 0.48 < 0.55
해결: Generator와 Creative Writer 프롬프트 개선
     - 강한 hook 추가
     - 감정적 공감 요소
     - 명확한 call-to-action
```

**2. Impressions 낮음**
```
문제: 도달 범위 자체가 작음
원인: Research layer의 트렌드 식별 약함
해결: Research 프롬프트 개선
     - 실시간 트렌드 소스 추가
     - 타겟 청중 분석 강화
```

**3. Internal vs External 불일치**
```
문제: 내부 점수는 높지만 실제 성과 낮음
원인: Critic의 평가 기준이 실제 engagement와 맞지 않음
해결: Critic 프롬프트에 실제 성과 예측 요소 추가
```

## 🔧 고급 기능

### 프롬프트 롤백
```python
# 특정 버전으로 롤백
def rollback_prompt(layers, layer_name, target_version):
    layer_data = layers[layer_name]
    prompt_history = layer_data["prompt_history"]
    
    for entry in prompt_history:
        if entry["version"] == target_version:
            # 모든 버전 비활성화
            for hist in prompt_history:
                hist["is_active"] = False
            # 타겟 버전 활성화
            entry["is_active"] = True
            layer_data["current_version"] = target_version
            return entry["prompt"]
    return None

# 사용 예시
if analysis["prompt_version_effectiveness"]["generator_v2"]["high"] < 2:
    # v2가 실패했다면 v1으로 롤백
    old_prompt = rollback_prompt(data["layers"], "generator", 1)
    print(f"✅ generator를 v1으로 롤백: {old_prompt[:100]}...")
```

### A/B 테스팅
```python
# 두 프롬프트 버전 병렬 테스트
def ab_test_prompts(layer, version_a, version_b, num_contents=10):
    results_a = generate_contents(layer, version_a, num_contents // 2)
    results_b = generate_contents(layer, version_b, num_contents // 2)
    
    # 성과 비교
    engagement_a = calculate_avg_engagement(results_a)
    engagement_b = calculate_avg_engagement(results_b)
    
    winner = "A" if engagement_a > engagement_b else "B"
    return winner, engagement_a, engagement_b
```

## 📝 주의사항

1. **프롬프트 히스토리 유지**: `prompt_history` 배열을 절대 삭제하지 마세요. 롤백 및 분석에 필수적입니다.
2. **is_active 플래그 관리**: 항상 하나의 버전만 `is_active=true`여야 합니다.
3. **current_version 동기화**: `is_active=true`인 버전과 `current_version`이 일치해야 합니다.
4. **충분한 샘플**: 최소 10개 콘텐츠 누적 후 분석하세요.
5. **시간 간격**: 외부 메트릭 수집 후 24-48시간 대기하세요.
6. **점진적 개선**: 한 번에 3개 레이어까지만 수정하세요.
7. **Safety 우선**: Safety 점수가 0.8 미만이면 즉시 개선하세요.

## 🐛 문제 해결

### Agent가 JSON이 아닌 텍스트 반환
```python
# instruction에 강조된 대로 JSON만 반환해야 함
# 응답 파싱 전 검증
if not response.strip().startswith("{"):
    print("⚠️ Invalid response format")
    # 재시도 로직
```

### 프롬프트 버전 불일치
```python
# 콘텐츠 생성 시 항상 현재 버전 기록
content["prompt_versions"] = {
    layer: layer_data["current_version"]
    for layer, layer_data in data["layers"].items()
}
```

### is_active 플래그 불일치
```python
# 활성 프롬프트 가져오기
def get_active_prompt(layer_data):
    for entry in layer_data["prompt_history"]:
        if entry.get("is_active", False):
            return entry["prompt"]
    # fallback: 가장 최신 버전
    return layer_data["prompt_history"][-1]["prompt"] if layer_data["prompt_history"] else None
```

## 📚 참고 자료

- **schemas.py**: Pydantic 모델 정의
- **agent.py**: HR Agent 및 도구 구현
- **hr_input_with_actual_performance.json**: 입력 데이터 예제

---

**버전**: 1.0.0  
**마지막 업데이트**: 2025-10-12  
**작성자**: HR Validation Agent Team

