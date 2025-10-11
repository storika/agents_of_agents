# 🔄 Agents-for-Agents 워크플로우 가이드

## 실제 사용 시나리오: 당신의 트위터 계정을 바이럴 시키기

### 🎯 목표
- **하나의 계정**(당신의 트위터/LinkedIn/Reddit)에서 콘텐츠 발행
- **여러 에이전트**가 협력해서 고품질 콘텐츠 생성
- **외부 성과**(좋아요, 리트윗, 조회수) 기반으로 팀 최적화

---

## 📅 Iteration 사이클

### Iteration 1: 빈 팀으로 시작

#### Step 1: 초기 팀 구성
```bash
# 프로젝트 컨텍스트로 빈 팀 input
{
  "iteration": 0,
  "agents": [],
  "score_history": {
    "avg_overall": [],
    "dims_mean": {},
    "content_history": []
  },
  "project_goal": "Create viral tech content",
  "target_audience": "Young developers on Twitter",
  "content_focus": "Productivity hacks, career advice, surprising insights"
}
```

#### Step 2: HR Agent가 LLM으로 초기 팀 생성
```python
result = analyze_team_and_decide(json.dumps(team_state))
# → LLM이 3-5명의 초기 팀 제안 (e.g., Explainer, EngageCritic, Ideator)
```

#### Step 3: 에이전트 생성 및 콘텐츠 작성
```
[Writer 에이전트들이 초안 작성]
  Explainer: "Here's how async/await works..."
  Ideator: "What if we frame it as a common mistake?"

[Critic 에이전트들이 평가]
  EngageCritic: 
    clarity: 0.85
    novelty: 0.60
    shareability: 0.70
```

#### Step 4: 콘텐츠 발행
- 최종 콘텐츠를 **당신의 트위터 계정**에 포스팅
- 24-48시간 대기 (메트릭 누적)

---

### Iteration 2: 첫 번째 성과 분석

#### Step 1: 외부 메트릭 수집
```bash
# 트위터 API 또는 수동 수집
{
  "content_id": "post_001",
  "iteration": 1,
  "contributors": ["Explainer", "Ideator", "EngageCritic"],
  "internal_scores": {
    "clarity": 0.85,
    "novelty": 0.60,
    "shareability": 0.70,
    "overall": 0.72
  },
  "twitter_likes": 180,
  "twitter_retweets": 12,
  "twitter_replies": 8,
  "views": 2100,
  "click_through_rate": 0.04
}
```

**분석**:
- Engagement Rate: (180+12+8)/2100 = **9.5%** (양호)
- Viral Score: 12/2100 * 20 = **11%** (낮음)
- 문제: **novelty가 낮음** (0.60), shareability도 보통

#### Step 2: HR Agent 실행
```python
team_state["score_history"]["content_history"] = [post_001_data]
result = analyze_team_and_decide(json.dumps(team_state))

# HR Agent 결정:
# - Hire: "TrendSpotter" (novelty 개선)
# - Coach: Explainer에게 "더 신선한 각도로 접근"
```

#### Step 3: 팀 업데이트 및 다음 콘텐츠
```
[새로운 팀 구성]
  Explainer (코칭받음)
  Ideator
  TrendSpotter (신규 채용)
  EngageCritic

[다음 콘텐츠 작성]
  TrendSpotter: "Everyone talks about async/await wrong. Here's why..."
  Explainer: [코칭 반영] "A junior dev's mistake that cost us $10K..."
```

---

### Iteration 5: 바이럴 성공!

#### Step 1: 특정 에이전트가 참여한 콘텐츠가 바이럴됨
```json
{
  "content_id": "post_005_viral",
  "iteration": 5,
  "contributors": ["ViralHook", "Explainer", "EngageCritic"],
  "internal_scores": {
    "clarity": 0.78,
    "novelty": 0.85,
    "shareability": 0.95,
    "overall": 0.85
  },
  "twitter_likes": 3200,
  "twitter_retweets": 580,
  "twitter_replies": 145,
  "linkedin_reactions": 890,
  "linkedin_shares": 234,
  "views": 48000,
  "click_through_rate": 0.12
}
```

**분석**:
- Engagement Rate: **12%** (매우 높음!)
- Viral Score: **1.2% share rate** (바이럴!)
- **ViralHook 에이전트가 기여** → 이 스타일이 효과적!

#### Step 2: 에이전트 기여도 계산
```
👤 ViralHook:
   기여 콘텐츠: 1개
   평균 조회수: 48,000  ← 바이럴!

👤 Explainer:
   기여 콘텐츠: 5개
   평균 조회수: 14,820  ← 안정적

👤 EngageCritic:
   기여 콘텐츠: 5개
   평균 조회수: 14,820  ← 안정적
```

#### Step 3: HR Agent의 판단
```python
# HR Agent 분석:
# - ViralHook의 스타일이 매우 효과적
# - 유사한 에이전트 더 채용 또는
# - 다른 에이전트들에게 ViralHook 스타일 코칭
```

---

## 🔧 실전 구현

### 1. 콘텐츠 생성 파이프라인

```python
def generate_content(team_agents):
    """여러 에이전트가 협력해서 콘텐츠 생성"""
    # Step 1: Writers가 초안 작성
    drafts = []
    for agent in [a for a in team_agents if 'writer' in a.role]:
        draft = agent.generate(context)
        drafts.append(draft)
    
    # Step 2: Critics가 평가 및 피드백
    scored_drafts = []
    for draft in drafts:
        scores = {}
        for critic in [a for a in team_agents if 'critic' in a.role]:
            score = critic.evaluate(draft)
            scores.update(score)
        scored_drafts.append((draft, scores))
    
    # Step 3: 최고 점수 선택 또는 병합
    best_draft, best_scores = max(scored_drafts, key=lambda x: x[1]['overall'])
    
    return {
        "content": best_draft,
        "internal_scores": best_scores,
        "contributors": [a.name for a in team_agents]
    }
```

### 2. 외부 메트릭 수집

```python
def collect_external_metrics(tweet_id, wait_hours=48):
    """트위터 API로 메트릭 수집"""
    time.sleep(wait_hours * 3600)
    
    tweet = api.get_tweet(tweet_id, tweet_fields=[
        'public_metrics', 'non_public_metrics'
    ])
    
    return {
        "twitter_likes": tweet.public_metrics['like_count'],
        "twitter_retweets": tweet.public_metrics['retweet_count'],
        "twitter_replies": tweet.public_metrics['reply_count'],
        "views": tweet.non_public_metrics['impression_count']
    }
```

### 3. Utility 계산

```python
def calculate_agent_utility(agent_name, content_history):
    """에이전트의 utility를 기여한 콘텐츠 성과 기반으로 계산"""
    contributed_content = [
        c for c in content_history 
        if agent_name in c.contributors
    ]
    
    if not contributed_content:
        return 0.5  # 기본값
    
    # 최근 콘텐츠에 더 높은 가중치 (EMA)
    alpha = 0.3
    utility = 0.5
    for content in reversed(contributed_content):
        # 내부 점수 + 외부 성과 결합
        internal_score = content.internal_scores.get('overall', 0.5)
        external_score = (content.engagement_rate + content.viral_score) / 2
        combined_score = 0.6 * internal_score + 0.4 * external_score
        
        utility = alpha * combined_score + (1 - alpha) * utility
    
    return utility
```

### 4. 전체 루프

```python
def run_a4a_system():
    team_state = initialize_empty_team()
    
    for iteration in range(100):
        print(f"\n=== Iteration {iteration} ===")
        
        # 1. HR Agent가 팀 최적화
        decisions = hr_agent.decide(team_state)
        team_state = apply_decisions(team_state, decisions)
        
        # 2. 콘텐츠 생성
        content = generate_content(team_state['agents'])
        
        # 3. 발행
        tweet_id = post_to_twitter(content['content'])
        
        # 4. 외부 메트릭 수집 (48시간 후)
        external_metrics = collect_external_metrics(tweet_id, wait_hours=48)
        
        # 5. 콘텐츠 히스토리 업데이트
        content_performance = {
            "content_id": f"post_{iteration:03d}",
            "iteration": iteration,
            "contributors": content['contributors'],
            "internal_scores": content['internal_scores'],
            **external_metrics
        }
        team_state['score_history']['content_history'].insert(0, content_performance)
        
        # 6. 에이전트 utility 업데이트
        for agent in team_state['agents']:
            agent['utility'] = calculate_agent_utility(
                agent['name'], 
                team_state['score_history']['content_history']
            )
        
        # 7. 다음 iteration
        team_state['iteration'] = iteration + 1
```

---

## 📊 Input Format

### 완전한 team_state 예시

```json
{
  "iteration": 5,
  "agents": [
    {
      "name": "Explainer",
      "role": "writer.specialist",
      "utility": 0.72,
      "prompt_version": 1,
      "prompt_similarity": {"EngageCritic": 0.3},
      "last_scores": {
        "clarity": 0.85,
        "novelty": 0.55,
        "shareability": 0.60,
        "credibility": 0.80,
        "safety": 0.95,
        "overall": 0.75
      }
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
    "content_history": [
      {
        "content_id": "post_005_viral",
        "iteration": 5,
        "contributors": ["ViralHook", "Explainer", "EngageCritic"],
        "internal_scores": {
          "clarity": 0.78,
          "novelty": 0.85,
          "shareability": 0.95,
          "overall": 0.85
        },
        "twitter_likes": 3200,
        "twitter_retweets": 580,
        "views": 48000
      }
    ]
  },
  "failures": ["Post_003 too generic"],
  "core_roles": ["HRValidation", "Explainer", "EngageCritic"],
  "project_goal": "Create viral tech content",
  "target_audience": "Young developers on Twitter",
  "content_focus": "Productivity, career advice, surprising insights"
}
```

---

## 🎯 핵심 포인트

1. **하나의 계정, 여러 에이전트**: 모든 에이전트가 협력해서 콘텐츠 생성
2. **콘텐츠 중심**: 외부 메트릭은 콘텐츠당 측정
3. **기여도 추적**: `contributors` 필드로 누가 참여했는지 기록
4. **Utility 계산**: 에이전트가 기여한 콘텐츠들의 평균 성과
5. **LLM 기반 최적화**: HR Agent가 성과 데이터 보고 자동으로 팀 조정

---

**버전**: 0.5.0  
**업데이트**: 2025-10-11

