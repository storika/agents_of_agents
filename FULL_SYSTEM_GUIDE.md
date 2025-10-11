# 🎯 전체 시스템 가이드: Mason 바이럴 시스템

## 개요

**목표**: Mason을 Twitter에서 바이럴시키기  
**방법**: AI 에이전트 팀이 협력하여 콘텐츠 생성 → 발행 → 분석 → 팀 최적화 반복

---

## 🔄 Iteration 흐름 (48시간 사이클)

```
┌─────────────────────────────────────────────────────────────┐
│  Iteration N (48시간 사이클)                                  │
└─────────────────────────────────────────────────────────────┘

1️⃣ HR Agent 실행 (5분)
   Input: team_state (이전 성과 포함)
   Output: hr_decisions (채용/제거/코칭)
   ↓
2️⃣ 결정 적용 (1분)
   - 새로운 에이전트 생성
   - 저성과 에이전트 제거
   - 프롬프트 개선
   ↓
3️⃣ 콘텐츠 생성 (30분)
   - 3개 트윗 생성
   - 각 트윗마다 3-5라운드 합의
   - Critics가 품질 검증
   ↓
4️⃣ Twitter 발행 (1분)
   - Mason 계정에 포스팅
   - Tweet ID 저장
   ↓
5️⃣ 대기 (24시간) ⏰
   - 트윗 확산 대기
   - 메트릭 누적
   ↓
6️⃣ 메트릭 수집 (5분)
   - Twitter API로 likes, retweets, views 수집
   - Engagement rate 계산
   ↓
7️⃣ 팀 상태 업데이트 (5분)
   - content_history에 성과 추가
   - 에이전트 utility 재계산
   - 평균 점수 업데이트
   ↓
8️⃣ 저장 및 대기 (24시간) ⏰
   - team_state JSON 저장
   - 다음 iteration까지 대기
   ↓
┌─────────────────────────────────────────────────────────────┐
│  Iteration N+1 시작                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 데이터 흐름

### Input (iteration 시작)

```json
{
  "iteration": 5,
  "agents": [
    {
      "name": "ViralHook",
      "role": "writer.specialist",
      "utility": 0.88,  // 이전 성과 기반
      "last_scores": {...}
    }
  ],
  "score_history": {
    "avg_overall": [0.70, 0.75, 0.82, 0.85, 0.89],
    "dims_mean": {...},
    "content_history": [
      {
        "content_id": "tweet_004_00",
        "iteration": 4,
        "contributors": ["ViralHook", "TrendScout"],
        "internal_scores": {"overall": 0.89, ...},
        // 24시간 후 수집된 메트릭
        "twitter_likes": 3200,
        "twitter_retweets": 580,
        "views": 48000
      }
    ]
  },
  "project_goal": "Make Mason viral on Twitter",
  ...
}
```

### Processing

#### Step 1: HR Agent 분석
```python
# HR Agent가 분석:
# - 최근 콘텐츠 성과 (views, engagement)
# - 에이전트별 기여도 (utility)
# - 약점 차원 (예: novelty가 낮음)

# 결정:
hr_decisions = {
  "hire_plan": [
    {
      "name": "ContrarianTake",
      "role": "writer.specialist",
      "system_prompt": "...",
      "reason": "Improve novelty (current: 0.65 → target: 0.80)"
    }
  ],
  "prune_list": [...],
  "prompt_feedback": [...]
}
```

#### Step 2: 에이전트 팀 구성
```python
agents = {
  "ViralHook": Agent(...),
  "TrendScout": Agent(...),
  "ContrarianTake": Agent(...)  # 새로 채용
}
```

#### Step 3: 콘텐츠 생성 (합의 기반)
```python
# Topic 1: "WeaveHack2 Day 5 progress"
Round 1:
  Writers 작성 → Critics 평가 (0.71) → 기준 미달
Round 2:
  Writers 개선 → Critics 재평가 (0.83) → ✅ 통과!

Result: 
  content = "Everyone thinks AI agents need supervision..."
  internal_scores = {overall: 0.83, novelty: 0.85, ...}
```

#### Step 4-6: 발행 & 메트릭 수집
```python
# Twitter API
tweet = client.create_tweet(text=content)
tweet_id = tweet.data["id"]

# 24시간 대기
time.sleep(24 * 3600)

# 메트릭 수집
metrics = client.get_tweet(tweet_id, tweet_fields=["public_metrics"])
# {likes: 3200, retweets: 580, views: 48000}
```

### Output (iteration 종료)

```json
{
  "iteration": 6,  // +1
  "agents": [
    {
      "name": "ViralHook",
      "utility": 0.91,  // 업데이트됨! (성과 반영)
      ...
    },
    {
      "name": "ContrarianTake",  // 신규
      "utility": 0.75,
      ...
    }
  ],
  "score_history": {
    "avg_overall": [..., 0.89, 0.91],  // 향상됨!
    "content_history": [
      // 최신 3개 콘텐츠 추가됨
      {
        "content_id": "tweet_005_02",
        "iteration": 5,
        "contributors": ["ContrarianTake", "ViralHook"],
        "internal_scores": {overall: 0.91, novelty: 0.92},
        "twitter_likes": 5200,  // 향상!
        "twitter_retweets": 980,
        "views": 72000
      },
      ...
    ]
  }
}
```

---

## 🚀 실행 방법

### Option 1: 자동 실행 (추천)

```bash
cd /Users/mason/workspace/agents_of_agents
python orchestrator.py
```

**특징**:
- 무한 루프 (최대 100 iterations)
- 48시간마다 자동 실행
- Ctrl+C로 중단 가능
- 모든 state가 JSON으로 저장됨

### Option 2: 수동 실행 (테스트용)

```bash
# Iteration 0: 초기 팀 생성
python agent_factory.py
# → hr_decisions_iteration_0.json 생성

# Iteration 1: 콘텐츠 생성
python content_generator.py
# → 3개 트윗 생성

# Twitter 발행 (수동)
# → Tweet IDs 기록

# 24시간 대기...

# 메트릭 수집 (수동)
# → team_state 업데이트

# Iteration 2: HR Agent 재실행
python agent_factory.py
```

### Option 3: 스케줄링 (프로덕션)

#### Cron (Linux/Mac)
```bash
# crontab -e
0 */48 * * * cd /path/to/agents_of_agents && python orchestrator.py >> logs/orchestrator.log 2>&1
```

#### systemd (Linux)
```ini
# /etc/systemd/system/mason-viral.service
[Unit]
Description=Mason Viral System

[Service]
Type=simple
WorkingDirectory=/path/to/agents_of_agents
ExecStart=/usr/bin/python3 orchestrator.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### PM2 (Node.js ecosystem)
```bash
pm2 start orchestrator.py --name mason-viral --interpreter python3
pm2 logs mason-viral
```

---

## 🎯 시나리오별 가이드

### Scenario 1: 완전히 처음 시작

```bash
# 1. 빈 팀으로 시작
python orchestrator.py

# 출력:
# Iteration 0:
#   HR Agent: 초기 팀 4명 제안 (ViralHook, TrendScout, EngageCritic, MasonVoice)
#   콘텐츠 생성: 3개
#   Twitter 발행
#   24시간 대기...
#   메트릭 수집: (평균 2000 views)
#
# Iteration 1:
#   HR Agent: novelty 낮음 → ContrarianTake 채용
#   콘텐츠 생성: 3개 (novelty 개선됨)
#   Twitter 발행
#   ...
```

### Scenario 2: 중간에 재시작

```bash
# 마지막 저장된 state 사용
python orchestrator.py

# orchestrator.py가 자동으로:
# - team_state_iteration_XXX.json 중 최신 파일 로드
# - 해당 iteration부터 재개
```

### Scenario 3: 수동 개입

```python
# team_state_iteration_005.json 수정
{
  "iteration": 5,
  "agents": [...],
  "failures": [
    "Tweet_004_02 was too technical - lost audience engagement"
  ],  // ← 실패 사례 추가
  ...
}

# 다음 iteration에서 HR Agent가 failures 학습
```

---

## 📈 성과 모니터링

### 1. Weave Dashboard

**https://wandb.ai/mason-choi-storika/WeaveHacks2/weave**

확인할 수 있는 것:
- **Calls**: 모든 함수 실행 (HR 결정, 콘텐츠 생성)
- **Traces**: Iteration별 전체 흐름
- **Models**: 에이전트 버전 히스토리
- **Datasets**: 콘텐츠 성과 기록

### 2. 로컬 JSON 파일

```bash
# Iteration별 상태
ls team_state_iteration_*.json

# 최신 상태 확인
cat team_state_iteration_010.json | jq '.score_history.avg_overall'
# [0.70, 0.75, 0.82, 0.85, 0.89, 0.91, ...]

# 바이럴 콘텐츠 찾기
cat team_state_iteration_010.json | jq '.score_history.content_history[] | select(.views > 50000)'
```

### 3. 실시간 모니터링

```bash
# orchestrator 로그 tail
tail -f orchestrator.log

# 또는 Python에서
python -c "
import json
with open('team_state_iteration_010.json') as f:
    data = json.load(f)
    
print(f'Iteration: {data[\"iteration\"]}')
print(f'Team size: {len(data[\"agents\"])}')
print(f'Avg score: {data[\"score_history\"][\"avg_overall\"][-1]:.2f}')
print(f'Best content: {max(data[\"score_history\"][\"content_history\"], key=lambda x: x[\"views\"])[\"content_id\"]}')
"
```

---

## ⚙️ 설정 조정

### orchestrator.py config

```python
config = {
    # ===== 타이밍 =====
    "iteration_interval_hours": 48,  # Iteration 간격
    "min_wait_for_metrics": 24,      # 최소 메트릭 대기
    
    # ===== 콘텐츠 =====
    "content_per_iteration": 3,      # Iteration당 콘텐츠 수
    
    # ===== 시스템 =====
    "max_iterations": 100,           # 최대 반복
}
```

### 빠른 테스트 모드

```python
# orchestrator.py 수정
config = {
    "iteration_interval_hours": 0.1,  # 6분 (테스트용)
    "min_wait_for_metrics": 0.05,     # 3분
    "content_per_iteration": 1,
    "max_iterations": 5
}
```

---

## 🐛 트러블슈팅

### Q: Iteration이 너무 느려요
```python
# 병렬 처리 추가 (orchestrator.py 수정)
from concurrent.futures import ThreadPoolExecutor

# Step 3에서:
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(generator.generate, topic) for topic in topics]
    contents = [f.result() for f in futures]
```

### Q: Twitter API 없어요
```python
# Mock mode로 실행 (이미 구현됨)
# orchestrator.py의 _post_to_twitter, _collect_twitter_metrics는 mock 지원
```

### Q: 중간에 중단했어요
```bash
# 마지막 저장된 iteration부터 재개
python orchestrator.py  # 자동으로 최신 state 로드
```

### Q: 특정 iteration부터 다시 실행하고 싶어요
```python
# orchestrator.py 수정
initial_team_state = json.load(open("team_state_iteration_005.json"))
orchestrator.run(initial_team_state)
```

---

## 📝 요약

| 단계 | 소요 시간 | 역할 |
|------|----------|------|
| 1. HR Agent | 5분 | 팀 최적화 결정 |
| 2. 결정 적용 | 1분 | 에이전트 생성/제거 |
| 3. 콘텐츠 생성 | 30분 | 3개 트윗, 합의 기반 |
| 4. Twitter 발행 | 1분 | API 호출 |
| 5. 대기 | 24시간 | 메트릭 누적 ⏰ |
| 6. 메트릭 수집 | 5분 | Twitter API |
| 7. 상태 업데이트 | 5분 | team_state 갱신 |
| 8. 대기 | 24시간 | 다음 iteration ⏰ |
| **Total** | **48시간** | **1 iteration** |

**결과**: 48시간마다 팀이 개선되고, 콘텐츠 품질이 향상되고, Mason이 점점 더 바이럴됩니다! 🚀

---

**Version**: 1.0.0  
**Date**: 2025-10-11  
**For**: Mason's Viral Journey 🐝

