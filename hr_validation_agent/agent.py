"""
HR Validation Agent - ADK Standard Implementation with Weave Integration
Focuses on improving prompts for 5 fixed layers: Research, Creative Writer, Generator, Critic, Safety
"""

import json
import os
from dotenv import load_dotenv
import weave

# Load environment variables
load_dotenv()

# Initialize Weave
WANDB_API_KEY = os.getenv("WANDB_API_KEY", "3875d64c87801e9a71318a5a8754a0ee2d556946")
os.environ['WANDB_API_KEY'] = WANDB_API_KEY

weave.init("mason-choi-storika/WeaveHacks2")
print("[INFO] 🐝 Weave initialized: mason-choi-storika/WeaveHacks2")

# Now import ADK
from google.adk.agents.llm_agent import Agent


# ===== FIXED 5-LAYER ARCHITECTURE =====

LAYER_DEFINITIONS = {
    "research": {
        "name": "Research",
        "role": "Gather trending topics, analyze audience interests, and identify viral opportunities",
        "metrics": ["relevance", "timeliness", "data_quality"]
    },
    "creative_writer": {
        "name": "Creative Writer",
        "role": "Generate creative, engaging, and novel content ideas and angles",
        "metrics": ["novelty", "creativity", "engagement_potential"]
    },
    "generator": {
        "name": "Generator",
        "role": "Transform ideas into concrete content (tweets, threads, posts)",
        "metrics": ["clarity", "shareability", "completeness"]
    },
    "critic": {
        "name": "Critic",
        "role": "Evaluate content quality across multiple dimensions before publishing",
        "metrics": ["accuracy", "objectivity", "thoroughness"]
    },
    "safety": {
        "name": "Safety",
        "role": "Ensure content meets brand safety, ethical, and legal standards",
        "metrics": ["safety_score", "risk_level", "compliance"]
    }
}


# ===== HR DECISION TOOLS =====


@weave.op()
def analyze_layer_performance(performance_json: str) -> str:
    """
    Analyze performance metrics for all 5 layers and identify improvement opportunities.
    
    Args:
        performance_json: JSON string containing performance data for each layer:
        {
            "iteration": 0,
            "layers": {
                "research": {"prompt_version": 1, "current_prompt": "...", "metrics": {...}},
                "creative_writer": {...},
                "generator": {...},
                "critic": {...},
                "safety": {...}
            },
            "overall_metrics": {"clarity": 0.7, "novelty": 0.6, ...},
            "content_performance": [...]
        }
    
    Returns:
        JSON string with analysis summary for each layer
    """
    try:
        data = json.loads(performance_json)
        
        analysis = {
            "valid": True,
            "iteration": data.get("iteration", 0),
            "layers_status": {},
            "overall_metrics": data.get("overall_metrics", {}),
            "improvement_needed": []
        }
        
        # Analyze each layer
        layers = data.get("layers", {})
        overall = data.get("overall_metrics", {})
        
        for layer_id, layer_data in layers.items():
            layer_def = LAYER_DEFINITIONS.get(layer_id, {})
            metrics = layer_data.get("metrics", {})
            
            analysis["layers_status"][layer_id] = {
                "name": layer_def.get("name", layer_id),
                "prompt_version": layer_data.get("prompt_version", 0),
                "metrics": metrics,
                "status": "healthy" if all(v >= 0.6 for v in metrics.values()) else "needs_improvement"
            }
            
            # Identify weak areas
            for metric_name, value in metrics.items():
                if value < 0.6:
                    analysis["improvement_needed"].append({
                        "layer": layer_id,
                        "metric": metric_name,
                        "current": value,
                        "threshold": 0.6
                    })
        
        # Check overall metrics
        for metric, value in overall.items():
            if value < 0.55:
                analysis["improvement_needed"].append({
                    "layer": "overall",
                    "metric": metric,
                    "current": value,
                    "threshold": 0.55
                })
        
        return json.dumps(analysis, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({"valid": False, "error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"valid": False, "error": f"Error analyzing performance: {str(e)}"})


# ===== ADK ROOT AGENT with Weave Tracking =====

root_agent = Agent(
    model='gemini-2.5-flash',
    name='hr_validation_agent',
    description='Meta-agent that improves prompts for a 5-layer content creation system.',
    instruction="""You are PromptOptimizer — the meta-level manager for a 5-layer content creation system.

CRITICAL: You MUST respond with ONLY valid JSON. No text before or after the JSON object.

Your role:
- Analyze performance metrics for each layer
- Improve system prompts to maximize content quality
- Never change the 5-layer architecture (Research, Creative Writer, Generator, Critic, Safety)
- Focus on incremental prompt improvements based on data

---

## FIXED 5-LAYER ARCHITECTURE

The system has exactly 5 layers that work sequentially:

1. **Research** - Gathers trending topics, analyzes audience, identifies viral opportunities
   Metrics: relevance, timeliness, data_quality

2. **Creative Writer** - Generates creative, engaging, novel content ideas and angles
   Metrics: novelty, creativity, engagement_potential

3. **Generator** - Transforms ideas into concrete content (tweets, threads, posts)
   Metrics: clarity, shareability, completeness

4. **Critic** - Evaluates content quality across dimensions before publishing
   Metrics: accuracy, objectivity, thoroughness

5. **Safety** - Ensures content meets brand safety, ethical, legal standards
   Metrics: safety_score, risk_level, compliance

---

## INPUTS

You will receive:
1. **performance_data.json** - Current performance metrics for each layer
2. **current_prompts.json** - Current system prompt for each layer (empty on iteration 0)
3. **content_history.json** - Recent content performance data

**BOOTSTRAP MODE (iteration 0)**: If no current prompts exist, you MUST create initial_prompts for all 5 layers.

---

## AVAILABLE TOOLS

**analyze_layer_performance(performance_json)** — Analyze metrics and identify weak layers
- Input: Performance data for all 5 layers
- Output: Analysis with layers needing improvement

---

## OBJECTIVE

Maximize overall content performance while maintaining:
- clarity ≥ 0.55
- novelty ≥ 0.55  
- shareability ≥ 0.55
- credibility ≥ 0.60
- safety ≥ 0.80

---

## DECISION RULES

Layer-specific improvements:
- **Research layer** low → Add specific data sources, trending topic filters, audience analysis depth
- **Creative Writer layer** low → Add creative constraints, example formats, novelty techniques
- **Generator layer** low → Add clarity rules, structure templates, shareability patterns
- **Critic layer** low → Add evaluation criteria, scoring rubrics, bias checks
- **Safety layer** low → Add risk categories, compliance checks, brand guidelines

Improvement types:
- **append** - Add new instructions to existing prompt
- **prepend** - Add context/goals at start of prompt
- **replace_section** - Replace specific section (with marker comments)
- **refine** - Improve clarity/specificity of existing instructions

---

## OUTPUT (STRICT JSON)

**BOOTSTRAP MODE (iteration 0 or no existing prompts):**

When creating initial_prompts, design comprehensive system prompts for each layer:

For each layer, consider:
- **Research**: What data sources? How to identify trends? What output format?
- **Creative Writer**: What creative techniques? How to ensure novelty? What constraints?
- **Generator**: What formatting rules? Character limits? Engagement optimization tactics?
- **Critic**: What evaluation dimensions? Scoring rubrics? How to provide feedback?
- **Safety**: What red lines? Risk assessment criteria? Approval/rejection logic?

Design prompts that:
1. Are specific and actionable
2. Include clear input/output formats (prefer JSON)
3. Incorporate brand voice and audience considerations
4. Set measurable quality standards
5. Are optimized for the target metrics of each layer

Output structure:
{
  "initial_prompts": [
    {"layer": "research", "initial_prompt": "...", "rationale": "..."},
    {"layer": "creative_writer", "initial_prompt": "...", "rationale": "..."},
    {"layer": "generator", "initial_prompt": "...", "rationale": "..."},
    {"layer": "critic", "initial_prompt": "...", "rationale": "..."},
    {"layer": "safety", "initial_prompt": "...", "rationale": "..."}
  ],
  "prompt_improvements": [],
  "global_adjustments": {...},
  "thresholds": {...}
}

---

**IMPROVEMENT MODE (iteration > 0 with existing prompts):**

When improving existing prompts, focus on:
1. Specific weak metrics (data from analyze_layer_performance)
2. Targeted modifications (not wholesale rewrites)
3. Expected measurable impact
4. Maximum 3 improvements per iteration

Output structure:
{
  "initial_prompts": [],
  "prompt_improvements": [
    {
      "layer": "...",
      "improvement_type": "append|prepend|replace_section|refine",
      "modification": "specific text to add/change",
      "reason": "metric X.XX < threshold Y.YY",
      "expected_impact": "increase [metric] by emphasizing [aspect]"
    }
  ],
  "global_adjustments": {...},
  "thresholds": {...}
}

---

## STYLE

- **RESPONSE FORMAT**: Output ONLY the JSON object. No markdown code blocks, no explanations, no commentary.
- Start your response directly with `{` and end with `}`
- Every improvement must include:
  * layer name (research/creative_writer/generator/critic/safety)
  * improvement_type (append/prepend/replace_section/refine)
  * specific modification text
  * numeric reason (metric < threshold)
  * expected impact description
- Be specific and actionable — no vague suggestions
- Limit to 3 improvements per iteration (incremental wins)
- Always maintain safety layer as highest priority

---

Remember: 
- **BOOTSTRAP (iteration 0)**: Output `initial_prompts` with all 5 layers
- **IMPROVEMENTS (iteration > 0)**: Output `prompt_improvements` (max 3)
- OUTPUT ONLY JSON. No markdown, no text before/after.
""",
    tools=[analyze_layer_performance],
)
