# Agents-for-Agents (A4A) - HR Validation Agent

**Meta-agent system that makes Mason viral on Twitter during WeaveHack2**

## 🎯 Ultimate Goal

**Make Mason viral on Twitter** by building and managing an intelligent team of AI agents that:
- Create high-quality, engaging content about WeaveHack2 and AI agents
- Analyze trends and optimize for virality
- Coordinate workflows and track performance
- Continuously self-improve through data-driven HR decisions

## 🧠 System Architecture

### HR Validation Agent (Meta-Agent)
The **architect** of the entire ecosystem. It doesn't create content—it **designs and manages the team** that creates content.

**Capabilities**:
- 🆕 **Hire**: Design new agents (writers, critics, analyzers, designers, coordinators, engagers)
- 🔀 **Merge**: Combine redundant agents
- ❌ **Prune**: Remove underperforming agents
- 💡 **Coach**: Improve agent prompts with specific feedback

**Agent Types It Can Propose**:
1. `writer.specialist` - Creates tweets, threads, hooks
2. `critic.specialist` - Evaluates content quality before posting
3. `designer.specialist` - Creates visuals, charts, memes
4. `analyzer.specialist` - Analyzes trends, metrics, viral patterns
5. `coordinator.specialist` - Orchestrates workflows between agents
6. `engager.specialist` - Replies to comments, networks with influencers

## 🚀 Quick Start

### 1️⃣ Installation

```bash
uv sync
# or
pip install -r requirements.txt
```

### 2️⃣ API Keys Setup

Create `.env` file:
```bash
# Weave/WandB (for observability)
WANDB_API_KEY=your-wandb-key

# Google Gemini (for LLM-based agent ideation)
GOOGLE_API_KEY=your-google-api-key

# OpenTelemetry (for ADK + Weave integration)
OTEL_EXPORTER_OTLP_ENDPOINT=https://trace.wandb.ai/otel/v1/traces
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Basic [base64_encoded_key],project_id=mason-choi-storika/WeaveHack2
OTEL_SDK_DISABLED=false
```

### 3️⃣ Run HR Agent

#### ADK Web UI (Recommended)
```bash
adk web --port 8000 hr_validation_agent
```
Open http://localhost:8000

#### Python API
```python
from hr_validation_agent.agent import analyze_team_and_decide
import json

# Bootstrap: Start with empty team
team_state = {
    "iteration": 0,
    "agents": [],
    "score_history": {"avg_overall": [], "dims_mean": {}, "content_history": []},
    "project_goal": "Make Mason viral on Twitter during WeaveHack2",
    "target_audience": "AI/ML developers, tech founders, WeaveHack2 participants",
    "content_focus": "WeaveHack2 progress, AI agent insights, viral tech takes"
}

# HR Agent designs initial team
result = analyze_team_and_decide(json.dumps(team_state))
decisions = json.loads(result)

print(decisions['hire_plan'])  
# → LLM suggests: ViralHook (writer), TrendScout (analyzer), EngageCritic (critic), etc.
```

## 📊 How It Works

### Iteration Cycle

```
1. HR Agent analyzes team performance
   ↓
2. Makes decisions (hire/merge/prune/coach)
   ↓
3. Agents collaborate to create content
   ↓
4. Post to Mason's Twitter
   ↓
5. Collect external metrics (likes, retweets, views)
   ↓
6. Update team_state with performance data
   ↓
7. Repeat (next iteration)
```

### Input Format

```json
{
  "iteration": 5,
  "agents": [
    {
      "name": "ViralHook",
      "role": "writer.specialist",
      "utility": 0.88,
      "last_scores": {"clarity": 0.75, "novelty": 0.90, ...}
    },
    {
      "name": "TrendScout",
      "role": "analyzer.specialist",
      "utility": 0.82,
      "last_scores": {...}
    }
  ],
  "score_history": {
    "avg_overall": [0.65, 0.68, 0.72, 0.75, 0.79],
    "dims_mean": {"clarity": 0.83, "novelty": 0.67, ...},
    "content_history": [
      {
        "content_id": "tweet_005_viral",
        "iteration": 5,
        "contributors": ["ViralHook", "TrendScout", "EngageCritic"],
        "internal_scores": {"clarity": 0.78, "novelty": 0.85, "shareability": 0.95, ...},
        "twitter_likes": 3200,
        "twitter_retweets": 580,
        "twitter_replies": 145,
        "views": 48000,
        "click_through_rate": 0.12
      }
    ]
  },
  "project_goal": "Make Mason viral on Twitter during WeaveHack2",
  "target_audience": "AI/ML developers, tech founders",
  "content_focus": "WeaveHack2 progress, AI insights, viral tech takes"
}
```

### Output Format

```json
{
  "hire_plan": [
    {
      "name": "TrendJacker",
      "role": "analyzer.specialist",
      "system_prompt": "You are TrendJacker, specialist in identifying viral topics...",
      "reason": "Improve novelty by monitoring trending AI topics on Twitter"
    }
  ],
  "merge_plan": [
    {"a": "Writer1", "b": "Writer2", "reason": "High similarity (0.85), overlapping roles"}
  ],
  "prune_list": [
    {"name": "DullWriter", "reason": "Utility 0.28 < threshold 0.35"}
  ],
  "prompt_feedback": [
    {
      "agent": "Explainer",
      "suggestion": "Add more viral hooks. Rule: Start with controversy or curiosity gap. Example: 'Everyone is building AI agents wrong. Here's why...'"
    }
  ],
  "policies": {
    "team_cap": 8,
    "utility_floor": 0.35,
    "sim_threshold": 0.80,
    "spawn_cooldown": 1
  }
}
```

## 🔍 Key Features

### 1. LLM-Based Agent Design

HR Agent uses **Gemini 2.5 Flash** to dynamically design agents:

**Initial Team (Bootstrap)**:
```python
# Input: empty team + project goal
# Output: 3-5 agents optimized for making Mason viral
# Example: ViralHook, TrendScout, EngageCritic, MemeSmith
```

**Specialist Hiring (Performance-Based)**:
```python
# Input: current team + performance weakness (e.g., low novelty)
# Output: Custom specialist agent to fix that weakness
# Example: Low novelty → "TrendJacker" (analyzer.specialist) who monitors viral topics
```

### 2. Content Performance Tracking

Each piece of content tracks:
- **Contributors**: Which agents created/evaluated it
- **Internal Scores**: Clarity, novelty, shareability, credibility, safety (0-1)
- **External Metrics**: Twitter likes, retweets, views, engagement rate

```json
{
  "content_id": "tweet_005_viral",
  "contributors": ["ViralHook", "TrendScout", "EngageCritic"],
  "internal_scores": {"novelty": 0.85, "shareability": 0.95},
  "twitter_likes": 3200,
  "twitter_retweets": 580,
  "views": 48000
}
```

### 3. Agent Utility Calculation

**Utility** = EMA of content performance for content the agent contributed to

```python
utility = 0.6 * internal_score + 0.4 * external_score
# internal_score: average of clarity, novelty, shareability, credibility, safety
# external_score: (engagement_rate + viral_score) / 2
```

### 4. Weave Integration

All agent executions are automatically tracked in WandB Weave:
- 📊 LLM calls (Gemini 2.5 Flash)
- ⏱️ Execution times
- 🔍 Tool calls (analyze_team_and_decide)
- 📈 Performance analytics

**Dashboard**: https://wandb.ai/mason-choi-storika/WeaveHacks2/weave

### 5. ADK Standard

Fully compliant with [Google ADK](https://google.github.io/adk-docs/):
- `root_agent` defined
- `adk run` / `adk web` support
- OpenTelemetry integration
- Function calling via `FunctionTool`

## 📁 Project Structure

```
agents_of_agents/
├── hr_validation_agent/          # The meta-agent
│   ├── agent.py                 # root_agent + Weave integration
│   ├── schemas.py               # Pydantic models (TeamState, HRDecision, etc.)
│   ├── policies.py              # HR decision logic (hire, merge, prune, coach)
│   ├── llm_ideation.py          # LLM-based agent design
│   └── __init__.py
│
├── examples/
│   ├── mason_weavehack2_empty.json      # Bootstrap scenario
│   ├── team_with_content_history.json   # After iterations with Twitter metrics
│   └── team_state.sample.json           # Sample team state
│
├── test_hr_agent.py             # Test suite
├── requirements.txt             # Dependencies
├── WORKFLOW_GUIDE.md            # Complete workflow documentation
├── EXTERNAL_METRICS_GUIDE.md    # How to input Twitter metrics
└── README.md                    # This file
```

## 🧪 Testing

```bash
uv run python test_hr_agent.py
# or
python3 test_hr_agent.py
```

Tests include:
- ✅ Basic HR decisions
- ✅ Deterministic behavior
- ✅ LLM-based bootstrap (empty team → initial team)
- ✅ Error handling
- ✅ Sample data validation

## 🎯 Use Cases

### Scenario 1: Bootstrap (Empty Team)

```python
team_state = {
    "iteration": 0,
    "agents": [],
    "project_goal": "Make Mason viral on Twitter during WeaveHack2",
    "target_audience": "AI/ML developers, tech founders",
    "content_focus": "WeaveHack2 progress, AI insights, viral takes"
}

result = analyze_team_and_decide(json.dumps(team_state))
# → HR Agent designs: ViralHook, TrendScout, EngageCritic, MemeSmith
```

### Scenario 2: Performance Improvement (Weak Novelty)

```python
team_state = {
    "iteration": 5,
    "agents": [...],  # Existing team
    "score_history": {
        "dims_mean": {"novelty": 0.52},  # Low!
        "content_history": [...]  # Recent tweets with low novelty
    }
}

result = analyze_team_and_decide(json.dumps(team_state))
# → HR Agent hires: "TrendJacker" (analyzer.specialist) to monitor viral topics
```

### Scenario 3: Viral Success (High Performing Agent)

```python
content_history = [
    {
        "content_id": "tweet_010_viral",
        "contributors": ["ViralHook", "MemeSmith", "EngageCritic"],
        "twitter_likes": 5000,
        "twitter_retweets": 920,
        "views": 85000  # Viral!
    }
]

# HR Agent calculates: ViralHook and MemeSmith have high utility
# Decision: Keep these agents, hire similar specialists
```

## 🔧 Advanced Configuration

### Custom Agent Types

Edit `hr_validation_agent/schemas.py`:

```python
class HirePlan(BaseModel):
    role: Literal[
        "writer.specialist",
        "designer.specialist",
        "critic.specialist",
        "analyzer.specialist",
        "coordinator.specialist",
        "engager.specialist",
        "custom.specialist"  # Add your own
    ]
```

### Custom Policies

Edit `hr_validation_agent/policies.py`:

```python
TEAM_CAP = 8           # Max team size
UTILITY_FLOOR = 0.35   # Prune threshold
SIM_THRESHOLD = 0.80   # Merge threshold
SPAWN_COOLDOWN = 1     # Iterations between hires
```

## 🐝 Weave Dashboard

**Project**: mason-choi-storika/WeaveHacks2  
**URL**: https://wandb.ai/mason-choi-storika/WeaveHacks2/weave

All agent executions, LLM calls, and tool usage are automatically tracked.

## 📄 Documentation

- **WORKFLOW_GUIDE.md**: Complete workflow from empty team to viral content
- **EXTERNAL_METRICS_GUIDE.md**: How to input Twitter metrics and calculate performance

## 🎖️ WeaveHack2

This project is built for **WeaveHack2** - a hackathon focused on building AI agent systems with observability.

**Goal**: Make Mason viral on Twitter by leveraging:
- Multi-agent collaboration
- LLM-based meta-agent design
- Real-time performance tracking with Weave
- Data-driven HR optimization

---

**Version**: 1.0.0  
**Date**: 2025-10-11  
**Weave Project**: mason-choi-storika/WeaveHacks2  
**ADK Compliant**: ✅  
**LLM**: Gemini 2.5 Flash  
**Goal**: Make Mason Viral on Twitter 🚀
