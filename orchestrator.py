"""
🎯 전체 시스템 오케스트레이터
콘텐츠 생성 → Twitter 발행 → 메트릭 수집 → HR 결정 → 반복
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List
import weave
from dotenv import load_dotenv

load_dotenv()
weave.init("mason-choi-storika/WeaveHacks2")


class MasonViralOrchestrator(weave.Model):
    """
    Mason을 바이럴시키기 위한 전체 시스템 오케스트레이터.
    """
    
    config: Dict[str, Any]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            config=config or {
                "iteration_interval_hours": 48,  # 48시간마다 iteration
                "content_per_iteration": 3,      # iteration당 3개 콘텐츠
                "max_iterations": 100,           # 최대 100 iterations
                "min_wait_for_metrics": 24,      # 최소 24시간 메트릭 대기
            }
        )
    
    def run(self, initial_team_state: Dict[str, Any]):
        """
        전체 시스템 실행 (무한 루프).
        
        Args:
            initial_team_state: 초기 팀 상태 (빈 팀 또는 기존 팀)
        """
        team_state = initial_team_state
        agents = {}
        
        for iteration in range(self.config["max_iterations"]):
            print(f"\n{'='*70}")
            print(f"🔄 Iteration {iteration}")
            print(f"{'='*70}")
            print(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # ===== STEP 1: HR Agent가 팀 최적화 =====
            print(f"\n1️⃣ HR Agent 실행...")
            hr_decisions = self._run_hr_agent(team_state, iteration)
            
            # ===== STEP 2: 결정 적용 (에이전트 생성/제거/수정) =====
            print(f"\n2️⃣ HR 결정 적용...")
            agents = self._apply_hr_decisions(agents, hr_decisions)
            
            # ===== STEP 3: 콘텐츠 생성 (여러 개) =====
            print(f"\n3️⃣ 콘텐츠 생성 ({self.config['content_per_iteration']}개)...")
            contents = self._generate_contents(agents, team_state, iteration)
            
            # ===== STEP 4: Twitter 발행 =====
            print(f"\n4️⃣ Twitter 발행...")
            tweet_ids = self._post_to_twitter(contents, iteration)
            
            # ===== STEP 5: 메트릭 수집 대기 =====
            print(f"\n5️⃣ 메트릭 수집 대기 ({self.config['min_wait_for_metrics']}시간)...")
            self._wait_for_metrics(self.config["min_wait_for_metrics"])
            
            # ===== STEP 6: 외부 메트릭 수집 =====
            print(f"\n6️⃣ Twitter 메트릭 수집...")
            metrics = self._collect_twitter_metrics(tweet_ids)
            
            # ===== STEP 7: team_state 업데이트 =====
            print(f"\n7️⃣ 팀 상태 업데이트...")
            team_state = self._update_team_state(
                team_state, 
                contents, 
                metrics, 
                agents, 
                iteration + 1
            )
            
            # ===== STEP 8: 저장 및 로깅 =====
            self._save_state(team_state, iteration)
            
            print(f"\n✅ Iteration {iteration} 완료!")
            print(f"⏰ End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏳ 다음 iteration까지 {self.config['iteration_interval_hours']}시간 대기...")
            
            # 다음 iteration까지 대기 (첫 번째 대기 제외)
            if iteration < self.config["max_iterations"] - 1:
                remaining_wait = self.config["iteration_interval_hours"] - self.config["min_wait_for_metrics"]
                time.sleep(remaining_wait * 3600)
    
    def _run_hr_agent(self, team_state: Dict, iteration: int) -> Dict:
        """Step 1: HR Agent 실행"""
        from hr_validation_agent.agent import analyze_team_and_decide
        
        print(f"  📊 현재 팀: {len(team_state['agents'])}명")
        
        result_json = analyze_team_and_decide(json.dumps(team_state))
        decisions = json.loads(result_json)
        
        print(f"  ✅ HR 결정:")
        print(f"     채용: {len(decisions['hire_plan'])}명")
        print(f"     병합: {len(decisions['merge_plan'])}건")
        print(f"     제거: {len(decisions['prune_list'])}명")
        print(f"     코칭: {len(decisions['prompt_feedback'])}명")
        
        return decisions
    
    def _apply_hr_decisions(self, current_agents: Dict, hr_decisions: Dict) -> Dict:
        """Step 2: HR 결정 적용"""
        from agent_factory import apply_hr_decisions
        
        updated_agents = apply_hr_decisions(current_agents, hr_decisions, verbose=False)
        
        print(f"  ✅ 현재 팀: {len(updated_agents)}명")
        for name in list(updated_agents.keys())[:5]:
            print(f"     - {name}")
        if len(updated_agents) > 5:
            print(f"     ... 외 {len(updated_agents) - 5}명")
        
        return updated_agents
    
    def _generate_contents(
        self, 
        agents: Dict, 
        team_state: Dict, 
        iteration: int
    ) -> List[Dict]:
        """Step 3: 콘텐츠 생성"""
        from content_generator import ContentGenerator
        
        contents = []
        topics = self._get_topics_for_iteration(team_state, iteration)
        
        generator = ContentGenerator(agents, {
            "max_iterations": 3,
            "min_quality_score": 0.75,
            "min_safety_score": 0.9
        })
        
        for i, topic in enumerate(topics[:self.config["content_per_iteration"]]):
            print(f"  📝 콘텐츠 {i+1}/{self.config['content_per_iteration']}: {topic[:50]}...")
            
            content, rounds, scores = generator.generate(topic, verbose=False)
            
            contents.append({
                "content_id": f"tweet_{iteration:03d}_{i:02d}",
                "topic": topic,
                "content": content,
                "rounds": rounds,
                "internal_scores": scores,
                "contributors": list(agents.keys())  # 모든 에이전트가 협력
            })
            
            print(f"     ✅ {rounds}라운드, 점수: {scores['overall']:.2f}")
        
        return contents
    
    def _get_topics_for_iteration(self, team_state: Dict, iteration: int) -> List[str]:
        """Iteration에 맞는 토픽 생성"""
        base_topics = [
            "WeaveHack2 progress update - Day {iteration}",
            "Surprising insight from building AI agents",
            "Behind-the-scenes: Agent collaboration",
            "What we learned about {random_topic}",
            "Hot take: {contrarian_view}"
        ]
        
        # 실제로는 TrendScout 같은 analyzer agent가 생성
        # 현재는 mock
        return [
            f"WeaveHack2 Day {iteration}: Building self-optimizing agents",
            "The surprising truth about multi-agent systems",
            "How our HR agent improved content quality by 3x"
        ]
    
    def _post_to_twitter(self, contents: List[Dict], iteration: int) -> List[str]:
        """Step 4: Twitter 발행"""
        tweet_ids = []
        
        for i, content_data in enumerate(contents):
            # 실제로는 Twitter API 호출
            # 현재는 mock
            mock_tweet_id = f"mock_tweet_{iteration}_{i}_{int(time.time())}"
            
            print(f"  🐦 발행 {i+1}: {content_data['content'][:50]}...")
            print(f"     ID: {mock_tweet_id}")
            
            tweet_ids.append(mock_tweet_id)
            
            # 실제 Twitter API 예시:
            # import tweepy
            # tweet = client.create_tweet(text=content_data["content"])
            # tweet_ids.append(tweet.data["id"])
        
        return tweet_ids
    
    def _wait_for_metrics(self, hours: float):
        """Step 5: 메트릭 누적 대기"""
        print(f"  ⏳ {hours}시간 대기 중...")
        # 실제로는: time.sleep(hours * 3600)
        # 테스트용으로 짧게
        time.sleep(1)  # 1초만 대기 (테스트용)
        print(f"  ✅ 대기 완료")
    
    def _collect_twitter_metrics(self, tweet_ids: List[str]) -> List[Dict]:
        """Step 6: Twitter 메트릭 수집"""
        metrics = []
        
        for tweet_id in tweet_ids:
            # 실제로는 Twitter API 호출
            # 현재는 mock (랜덤 생성)
            import random
            views = random.randint(1000, 50000)
            likes = int(views * random.uniform(0.03, 0.12))
            retweets = int(likes * random.uniform(0.05, 0.15))
            
            metric = {
                "tweet_id": tweet_id,
                "twitter_likes": likes,
                "twitter_retweets": retweets,
                "twitter_replies": int(retweets * 0.5),
                "views": views,
                "click_through_rate": random.uniform(0.03, 0.10)
            }
            
            metrics.append(metric)
            
            print(f"  📊 {tweet_id}:")
            print(f"     👁️  {views:,} views")
            print(f"     ❤️  {likes:,} likes")
            print(f"     🔄 {retweets:,} retweets")
        
        return metrics
    
    def _update_team_state(
        self,
        team_state: Dict,
        contents: List[Dict],
        metrics: List[Dict],
        agents: Dict,
        next_iteration: int
    ) -> Dict:
        """Step 7: 팀 상태 업데이트"""
        
        # 1. content_history 업데이트
        for content, metric in zip(contents, metrics):
            performance = {
                "content_id": content["content_id"],
                "iteration": team_state["iteration"],
                "contributors": content["contributors"],
                "internal_scores": content["internal_scores"],
                **metric  # twitter_likes, twitter_retweets, etc.
            }
            team_state["score_history"]["content_history"].insert(0, performance)
        
        # 2. 평균 점수 업데이트
        if contents:
            avg_overall = sum(c["internal_scores"]["overall"] for c in contents) / len(contents)
            team_state["score_history"]["avg_overall"].append(avg_overall)
            
            # dims_mean 업데이트
            for dim in ["clarity", "novelty", "shareability", "credibility", "safety"]:
                scores = [c["internal_scores"].get(dim, 0.5) for c in contents]
                team_state["score_history"]["dims_mean"][dim] = sum(scores) / len(scores)
        
        # 3. 에이전트 상태 업데이트
        team_state["agents"] = []
        for name, agent in agents.items():
            # 에이전트 utility 계산 (기여한 콘텐츠의 성과 기반)
            utility = self._calculate_agent_utility(name, team_state["score_history"]["content_history"])
            
            team_state["agents"].append({
                "name": name,
                "role": getattr(agent, "description", "unknown"),
                "utility": utility,
                "prompt_version": 0,
                "prompt_similarity": {},
                "last_scores": contents[0]["internal_scores"] if contents else {}
            })
        
        # 4. Iteration 증가
        team_state["iteration"] = next_iteration
        
        print(f"  ✅ 팀 상태 업데이트 완료")
        print(f"     평균 점수: {team_state['score_history']['avg_overall'][-1]:.2f}")
        print(f"     콘텐츠 히스토리: {len(team_state['score_history']['content_history'])}개")
        
        return team_state
    
    def _calculate_agent_utility(self, agent_name: str, content_history: List[Dict]) -> float:
        """에이전트 utility 계산"""
        # 해당 에이전트가 기여한 콘텐츠만 필터
        contributed = [
            c for c in content_history 
            if agent_name in c.get("contributors", [])
        ]
        
        if not contributed:
            return 0.5
        
        # 최근 3개 콘텐츠의 EMA
        alpha = 0.3
        utility = 0.5
        
        for content in contributed[:3]:
            # 내부 점수 + 외부 성과 결합
            internal = content["internal_scores"]["overall"]
            external = (
                content.get("twitter_likes", 0) + content.get("twitter_retweets", 0)
            ) / max(content.get("views", 1), 1)
            
            combined = 0.6 * internal + 0.4 * min(external * 10, 1)  # external 정규화
            utility = alpha * combined + (1 - alpha) * utility
        
        return round(utility, 2)
    
    def _save_state(self, team_state: Dict, iteration: int):
        """Step 8: 상태 저장"""
        filename = f"team_state_iteration_{iteration:03d}.json"
        
        with open(filename, 'w') as f:
            json.dump(team_state, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 저장: {filename}")


# ===== 실행 스크립트 =====

def main():
    print("🚀 Mason Viral Orchestrator")
    print("=" * 70)
    
    # 1. 초기 팀 상태 로드
    try:
        with open("examples/mason_weavehack2_empty.json") as f:
            initial_team_state = json.load(f)
        print("✅ 초기 팀 상태 로드: examples/mason_weavehack2_empty.json")
    except FileNotFoundError:
        # 빈 팀으로 시작
        initial_team_state = {
            "iteration": 0,
            "agents": [],
            "score_history": {
                "avg_overall": [],
                "dims_mean": {},
                "content_history": []
            },
            "failures": [],
            "core_roles": ["HRValidation"],
            "project_goal": "Make Mason viral on Twitter during WeaveHack2",
            "target_audience": "AI/ML developers, tech founders, WeaveHack2 participants",
            "content_focus": "WeaveHack2 progress, AI insights, viral tech takes"
        }
        print("⚠️  초기 파일 없음 → 빈 팀으로 시작")
    
    # 2. Orchestrator 생성
    orchestrator = MasonViralOrchestrator({
        "iteration_interval_hours": 48,  # 실제: 48시간
        "content_per_iteration": 3,
        "max_iterations": 100,
        "min_wait_for_metrics": 24  # 실제: 24시간
    })
    
    # 3. 실행
    print("\n🎯 시스템 시작...")
    print("   - Iteration 간격: 48시간")
    print("   - Iteration당 콘텐츠: 3개")
    print("   - 메트릭 대기: 24시간")
    print()
    
    try:
        orchestrator.run(initial_team_state)
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 테스트 모드 (빠르게)
    print("🧪 테스트 모드 (빠른 실행)")
    print("실제 운영 시 orchestrator.py의 config 조정 필요")
    print()
    
    main()

