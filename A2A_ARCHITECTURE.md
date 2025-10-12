# A2A (Agent-to-Agent) Architecture

**Complete guide to the multi-agent system with A2A protocol**

---

## 🎯 Overview

This system implements an **Agent-to-Agent (A2A) protocol** for coordinating multiple specialized AI agents. The **CMO Agent** acts as a strategy orchestrator, deciding which specialist agent to call based on context, performance data, and user intent.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   CMO AGENT                             │
│          (Strategy Orchestrator)                        │
│                                                         │
│  Analyzes:                                              │
│  - Performance history                                  │
│  - Trending topics                                      │
│  - Strategy mix                                         │
│  - User intent                                          │
│                                                         │
│  Decides: POST | QUOTE | REPLY | REPOST                │
│  Delegates: Via A2A protocol                            │
└─────────────────────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┬──────────┐
          │            │            │          │
          ▼            ▼            ▼          ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
    │  POST   │  │ QUOTE   │  │ REPLY   │  │ REPOST  │
    │ AGENT   │  │ AGENT   │  │ AGENT   │  │ AGENT   │
    └─────────┘  └─────────┘  └─────────┘  └─────────┘
        │
        └─→ Research → Writer → Generator → Critic
            → Safety → Selector → Image Gen → Post
```

---

## 📋 Agent Roles

### **CMO Agent** (Strategy Orchestrator)
- **Purpose**: Decides WHAT action to take
- **Responsibilities**:
  - Analyze performance history
  - Monitor trending topics
  - Decide optimal strategy
  - Delegate to specialist agents via A2A
  - Learn from results
- **Tools**:
  - `analyze_performance_history()`
  - `get_trending_context()`
  - `call_post_agent()`
  - `call_quote_agent()`
  - `call_reply_agent()`
  - `call_repost_agent()`

### **Post Agent** (Content Creator)
- **Purpose**: Creates original tweets with images
- **Best for**: Showcasing progress, insights, announcements
- **Sub-agents**:
  - Research Agent (trend analysis)
  - Creative Writer (idea generation)
  - Generator (content creation)
  - Critic (quality evaluation)
  - Safety Agent (validation)
  - Selector (best candidate selection)
  - Image Generator (visual creation)
- **Output**: Tweet + Image + Performance prediction

### **Quote Agent** (Comment & Amplify)
- **Purpose**: Creates quote tweets with comments
- **Best for**: Community engagement, thought leadership
- **Workflow**:
  1. Find trending tweet
  2. Generate insightful comment
  3. Post quote tweet
- **Output**: Quote tweet with added commentary

### **Reply Agent** (Relationship Builder)
- **Purpose**: Creates thoughtful replies to tweets
- **Best for**: Building relationships, showing expertise
- **Strategies**: Insightful, Helpful, Engaging, Supportive, Informative
- **Output**: Reply with value-add content

### **Repost Agent** (Curator)
- **Purpose**: Simple reposts without comments
- **Best for**: Amplifying exceptional content
- **Criteria**: Alignment, Quality, Relevance, Authority, Timeliness
- **Output**: Simple repost with alignment analysis

---

## 🔗 A2A Protocol Specification

### Request Format

```python
{
    "action": str,              # Action to perform
    "params": {                 # Action-specific parameters
        "topic": str,           # (optional)
        "tone": str,            # (optional)
        "tweet_url": str,       # (optional)
        "strategy": str,        # (optional)
        "require_approval": bool
    },
    "context": {                # Shared context
        "trending_topics": [],
        "historical_performance": [],
        "recent_strategies": {}
    },
    "caller": str,              # Who's calling
    "timestamp": str            # ISO timestamp
}
```

### Response Format

```python
{
    "status": str,              # "success" | "pending" | "failed"
    "result": {                 # Action result
        "content_generated": bool,
        "response": str,
        "requires_approval": bool
    },
    "metadata": {
        "agent": str,           # Agent name
        "action": str,          # Action performed
        "timestamp": str,       # ISO timestamp
        "metrics": {
            "generation_time_ms": int,
            "internal_scores": {},
            "engagement_prediction": float
        }
    }
}
```

---

## 🚀 Usage Examples

### Example 1: CMO Decides Strategy

```python
from cmo_agent.agent import decide_and_execute

# User request - CMO decides best strategy
response = decide_and_execute("Create next viral content")

# CMO analyzes:
# - Performance history: Last 5 actions = [post, post, post, quote, post]
# - Trending topics: "AI Agents" trending high
# - Decision: QUOTE (diversify from overused POST strategy)
# - Delegates to quote_agent via A2A
```

### Example 2: Direct Agent Call

```python
from post_agent.agent import create_post

# Direct call to post_agent (bypassing CMO)
result = create_post(
    topic="Multi-Agent Systems",
    tone="witty",
    context={"trending_topics": ["AI", "Agents"]}
)
```

### Example 3: A2A Protocol Call

```python
from cmo_agent.tools import call_agent_via_a2a

# Universal A2A call
response = call_agent_via_a2a(
    agent_name="quote_agent",
    action="create_quote_tweet",
    params={"strategy": "trending", "require_approval": True},
    context={"trending_topics": ["AI Agents"]}
)
```

---

## 📊 Strategy Decision Logic

### Decision Factors

1. **Performance History** (40% weight)
   - Which strategies performed best?
   - What's the current mix?
   - What patterns are emerging?

2. **Trending Context** (30% weight)
   - What topics are hot?
   - Best format for topics?
   - Conversation to join?

3. **Content Diversity** (20% weight)
   - Optimal mix: 40% post, 35% quote, 20% reply, 5% repost
   - Avoid > 3 same type in a row
   - Balance original vs engagement

4. **Timing** (10% weight)
   - Peak times: 9-11 AM PST, 3-5 PM PST
   - Space out by 2-4 hours
   - Coordinate with content type

### Example Decision Flow

```
INPUT: "Create next viral content"

STEP 1: ANALYZE
├─ analyze_performance_history()
│  └─ Last 5: [post, post, post, quote, post]
│     Quote engagement: 0.067 vs Post: 0.042
│
└─ get_trending_context()
   └─ "AI Agents" trending (0.92 score)

STEP 2: DECIDE
├─ Post strategy overused (4/5 recent)
├─ Quote performing 60% better
├─ "AI Agents" perfect for quote tweet
└─ DECISION: QUOTE ✓

STEP 3: EXECUTE
call_quote_agent(
    strategy="trending",
    context={
        "trending_topics": ["AI Agents"],
        "preferred_tone": "witty"
    }
)

STEP 4: REPORT
"Decided QUOTE because:
1. Post overused (4/5 recent)
2. Quote tweets +60% engagement
3. Perfect trending topic match"
```

---

## 🛠️ Implementation Details

### File Structure

```
agents_of_agents/
├── cmo_agent/                    # Strategy Orchestrator
│   ├── agent.py                 # NEW: Strategy decision logic
│   ├── agent.py.backup          # Original (ContentPipeline)
│   ├── tools.py                 # NEW: A2A protocol layer
│   ├── tools.py.backup          # Original (x_publish, etc.)
│   ├── sub_agents.py            # MOVED to post_agent/
│   └── __init__.py
│
├── post_agent/                   # NEW: Original content creator
│   ├── agent.py                 # Root agent + A2A execute()
│   ├── sub_agents.py            # All content generation subagents
│   ├── tools.py                 # x_publish, image generation
│   └── __init__.py
│
├── quote_agent/                  # Quote tweets (UPDATED)
│   ├── agent.py                 # ADDED: execute() A2A interface
│   ├── tools.py                 # Existing tools
│   └── __init__.py              # UPDATED: export execute
│
├── reply_agent/                  # NEW: Thoughtful replies
│   ├── agent.py                 # Root agent + A2A execute()
│   ├── tools.py                 # Reply generation tools
│   └── __init__.py
│
└── repost_agent/                 # NEW: Simple reposts
    ├── agent.py                 # Root agent + A2A execute()
    ├── tools.py                 # Repost tools
    └── __init__.py
```

### Key Changes from Original

**Before** (Monolithic):
- cmo_agent had ContentPipeline subagents
- Direct content generation and posting
- No strategy decision layer

**After** (A2A):
- cmo_agent is pure strategy orchestrator
- ContentPipeline moved to post_agent
- All agents follow A2A protocol
- Clear separation: strategy vs execution

---

## 🧪 Testing

### Test A2A Integration

```python
# test_a2a_integration.py

def test_cmo_calls_post_agent():
    """Test CMO → post_agent via A2A"""
    from cmo_agent.agent import decide_and_execute

    response = decide_and_execute("Create an original post about AI agents")
    assert "post_agent" in str(response)
    print("✅ CMO successfully delegated to post_agent")

def test_cmo_calls_quote_agent():
    """Test CMO → quote_agent via A2A"""
    from cmo_agent.agent import decide_and_execute

    response = decide_and_execute("Find a trending tweet and quote it")
    assert "quote_agent" in str(response)
    print("✅ CMO successfully delegated to quote_agent")

def test_direct_a2a_call():
    """Test direct A2A protocol call"""
    from cmo_agent.tools import call_agent_via_a2a

    response = call_agent_via_a2a(
        agent_name="post_agent",
        action="create_post",
        params={"topic": "AI", "tone": "witty"},
        context={}
    )

    assert response["status"] == "success"
    assert response["metadata"]["agent"] == "post_agent"
    print("✅ Direct A2A call successful")

if __name__ == "__main__":
    test_cmo_calls_post_agent()
    test_cmo_calls_quote_agent()
    test_direct_a2a_call()
    print("\n🎉 All A2A tests passed!")
```

### Run via ADK Web UI

```bash
# Test post_agent independently
adk web --port 8000 post_agent

# Test CMO orchestration
adk web --port 8001 cmo_agent

# Test quote_agent
adk web --port 8002 quote_agent
```

---

## 📈 Benefits of A2A Architecture

### 1. Separation of Concerns
- CMO decides **WHAT** (strategy)
- Specialists decide **HOW** (execution)
- Clear boundaries and responsibilities

### 2. Scalability
- Easy to add new agent types
- Independent development and testing
- Modular architecture

### 3. Performance Optimization
- CMO learns which strategies work best
- Dynamic strategy adjustment
- Data-driven decision making

### 4. Observability
- Clear A2A boundaries tracked in Weave
- Strategy metrics separate from execution
- End-to-end tracing

### 5. Reusability
- Agents can be called by other orchestrators
- Standalone agent deployment
- Flexible composition

---

## 🔮 Future Enhancements

### Phase 1: Enhanced Analytics
- Real-time performance tracking
- A/B testing different strategies
- Predictive engagement modeling

### Phase 2: More Agents
- **thread_agent**: Multi-tweet threads
- **meme_agent**: Meme generation
- **video_agent**: Short video clips
- **poll_agent**: Interactive polls

### Phase 3: Advanced Orchestration
- Multi-agent collaboration (post + reply combo)
- Scheduled content calendar
- Auto-optimization based on engagement

### Phase 4: Learning Loop
- Reinforcement learning from engagement
- Strategy mix optimization
- Persona adaptation

---

## 📚 Additional Resources

- **README.md**: Project overview
- **ITERATION_FLOW.md**: Original iteration workflow
- **CMO_X_POSTING_GUIDE.md**: X/Twitter posting guide
- **Weave Dashboard**: https://wandb.ai/mason-choi-storika/WeaveHacks2/weave

---

**Version**: 2.0.0
**Date**: 2025-10-11
**Architecture**: A2A Protocol
**Status**: Production Ready ✅
