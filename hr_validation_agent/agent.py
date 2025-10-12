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
from google.adk.agents.sequential_agent import SequentialAgent

# Import schemas for structured output
from hr_validation_agent.schemas import PromptOptimizationDecision

# Import CMO version management tools
from cmo_agent.tools_version import (
    apply_prompt_improvements,
    restore_cmo_version,
    list_cmo_versions,
    get_version_metadata
)

# Import prompt loader tools
from hr_validation_agent.tools_prompt_loader import (
    load_current_cmo_prompts,
    create_hr_input_from_posts
)


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
        # Try to parse with json-repair if direct parsing fails (optional dependency)
        try:
            data = json.loads(performance_json)
        except json.JSONDecodeError as parse_error:
            print(f"⚠️ [ANALYZE] Direct parse failed, trying json-repair: {str(parse_error)[:100]}")
            try:
                from json_repair import repair_json
                repaired = repair_json(performance_json)
                data = json.loads(repaired)
                print("✅ [ANALYZE] json-repair successful")
            except ImportError:
                print("ℹ️ [ANALYZE] json-repair not available, returning parse error")
                raise parse_error
            except Exception as repair_error:
                print(f"❌ [ANALYZE] json-repair also failed: {str(repair_error)[:100]}")
                raise parse_error  # Raise original error
        
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


def evaluate_content_engagement(content_engagement_json: str) -> str:
    """
    Evaluate the relationship between layer prompts and actual content engagement.
    Analyzes which prompt versions and characteristics lead to high engagement.
    
    Args:
        content_engagement_json: JSON string containing:
        {
            "layers": {
                "research": {
                    "current_version": 1,
                    "metrics": {...},
                    "prompt_history": [
                        {
                            "version": 1,
                            "prompt": "...",
                            "created_at": "...",
                            "reason": "...",
                            "is_active": true
                        }
                    ]
                },
                ...
            },
            "contents": [
                {
                    "content_id": "tweet_001",
                    "text": "actual content...",
                    "media_prompt": "...",
                    "hashtags": ["#AI", "#Agents"],
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
                        "clarity": 0.75, "novelty": 0.60, "shareability": 0.70,
                        "credibility": 0.80, "safety": 0.90
                    },
                    "actual_performance": {
                        "impressions": 48000,
                        "likes": 3200,
                        "retweets": 580,
                        "replies": 145,
                        "bookmarks": 420,
                        "profile_clicks": 890,
                        "url_clicks": 1200,
                        "engagement_rate": 0.097
                    }
                }
            ]
        }
    
    Returns:
        JSON string with engagement analysis, prompt version effectiveness, and recommendations
    """
    try:
        data = json.loads(content_engagement_json)
        
        # Support both HR input JSON structure and direct engagement data
        layers = data.get("layers", {})
        
        # Check for direct contents field (old format)
        contents = data.get("contents", [])
        
        # If no direct contents, extract from actual_engagement in layers (HR input format)
        if not contents:
            for layer_name, layer_data in layers.items():
                actual_engagement = layer_data.get("actual_engagement", {})
                layer_contents = actual_engagement.get("content", [])
                if layer_contents:
                    contents.extend(layer_contents)
        
        if not contents:
            return json.dumps({
                "valid": False,
                "error": "No content data provided"
            })
        
        # Calculate engagement statistics
        engagement_rates = []
        viral_scores = []
        high_performers = []  # engagement_rate > 0.05
        low_performers = []   # engagement_rate < 0.02
        
        for content in contents:
            perf = content.get("actual_performance", {})
            impressions = perf.get("impressions", 0)
            
            if impressions > 0:
                total_interactions = (
                    perf.get("likes", 0) +
                    perf.get("retweets", 0) +
                    perf.get("replies", 0) +
                    perf.get("bookmarks", 0)
                )
                engagement_rate = total_interactions / impressions
                engagement_rates.append(engagement_rate)
                
                # Calculate viral score (retweets primarily indicate virality)
                retweets = perf.get("retweets", 0)
                viral_score = min(1.0, (retweets / impressions) * 20)
                viral_scores.append(viral_score)
                
                # Categorize performance
                if engagement_rate > 0.05:
                    high_performers.append({
                        "content_id": content.get("content_id"),
                        "engagement_rate": engagement_rate,
                        "viral_score": viral_score,
                        "contributors": content.get("contributors", []),
                        "internal_scores": content.get("internal_scores", {})
                    })
                elif engagement_rate < 0.02:
                    low_performers.append({
                        "content_id": content.get("content_id"),
                        "engagement_rate": engagement_rate,
                        "viral_score": viral_score,
                        "contributors": content.get("contributors", []),
                        "internal_scores": content.get("internal_scores", {})
                    })
        
        # Calculate averages
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        avg_viral = sum(viral_scores) / len(viral_scores) if viral_scores else 0
        
        # Identify patterns in high performers
        high_perf_contributors = {}
        prompt_version_performance = {}  # Track performance by prompt version
        
        for hp in high_performers:
            for contributor in hp["contributors"]:
                if contributor not in high_perf_contributors:
                    high_perf_contributors[contributor] = 0
                high_perf_contributors[contributor] += 1
            
            # Track prompt version effectiveness
            prompt_vers = hp.get("prompt_versions", {})
            for layer, version in prompt_vers.items():
                key = f"{layer}_v{version}"
                if key not in prompt_version_performance:
                    prompt_version_performance[key] = {"high": 0, "low": 0}
                prompt_version_performance[key]["high"] += 1
        
        # Track low performers' prompt versions
        for lp in low_performers:
            prompt_vers = lp.get("prompt_versions", {})
            for layer, version in prompt_vers.items():
                key = f"{layer}_v{version}"
                if key not in prompt_version_performance:
                    prompt_version_performance[key] = {"high": 0, "low": 0}
                prompt_version_performance[key]["low"] += 1
        
        # Analyze internal score correlations with engagement
        score_correlations = {}
        for score_dim in ["clarity", "novelty", "shareability", "credibility", "safety"]:
            high_scores = [hp["internal_scores"].get(score_dim, 0) for hp in high_performers]
            low_scores = [lp["internal_scores"].get(score_dim, 0) for lp in low_performers]
            
            high_avg = sum(high_scores) / len(high_scores) if high_scores else 0
            low_avg = sum(low_scores) / len(low_scores) if low_scores else 0
            
            score_correlations[score_dim] = {
                "high_performer_avg": round(high_avg, 3),
                "low_performer_avg": round(low_avg, 3),
                "difference": round(high_avg - low_avg, 3),
                "impact": "strong" if abs(high_avg - low_avg) > 0.15 else "moderate" if abs(high_avg - low_avg) > 0.08 else "weak"
            }
        
        analysis = {
            "valid": True,
            "total_contents_analyzed": len(contents),
            "engagement_stats": {
                "avg_engagement_rate": round(avg_engagement, 4),
                "avg_viral_score": round(avg_viral, 4),
                "high_performers_count": len(high_performers),
                "low_performers_count": len(low_performers)
            },
            "layer_contribution_to_high_performance": high_perf_contributors,
            "prompt_version_effectiveness": prompt_version_performance,
            "internal_score_correlations": score_correlations,
            "insights": []
        }
        
        # Generate insights
        if avg_engagement < 0.03:
            analysis["insights"].append({
                "type": "low_engagement",
                "message": f"Overall engagement rate ({avg_engagement:.4f}) is below healthy threshold (0.03)",
                "recommendation": "Focus on improving shareability and novelty in creative_writer and generator layers"
            })
        
        if avg_viral < 0.3:
            analysis["insights"].append({
                "type": "low_virality",
                "message": f"Viral score ({avg_viral:.4f}) indicates content rarely gets shared",
                "recommendation": "Enhance research layer to identify more shareable trends and improve generator hooks"
            })
        
        # Find most impactful score dimensions
        sorted_correlations = sorted(
            score_correlations.items(),
            key=lambda x: abs(x[1]["difference"]),
            reverse=True
        )
        
        if sorted_correlations and abs(sorted_correlations[0][1]["difference"]) > 0.15:
            top_dim = sorted_correlations[0][0]
            diff = sorted_correlations[0][1]["difference"]
            analysis["insights"].append({
                "type": "strong_correlation",
                "message": f"{top_dim} shows strong correlation with engagement (Δ={diff:.3f})",
                "recommendation": f"Optimize prompts to maximize {top_dim} in relevant layers"
            })
        
        # Identify underperforming layers
        all_layers = set(layers.keys())
        contributing_layers = set(high_perf_contributors.keys())
        non_contributing = all_layers - contributing_layers
        
        if non_contributing:
            analysis["insights"].append({
                "type": "underperforming_layers",
                "message": f"Layers {list(non_contributing)} not contributing to high-performing content",
                "recommendation": f"Review and strengthen prompts for: {', '.join(non_contributing)}"
            })
        
        # Analyze prompt version performance with history context
        for prompt_key, perf in prompt_version_performance.items():
            total = perf["high"] + perf["low"]
            if total >= 2:  # Only analyze if enough samples
                success_rate = perf["high"] / total
                layer_name, version_str = prompt_key.split("_v")
                version_num = int(version_str)
                
                # Try to get prompt details from history
                prompt_details = None
                if layer_name in layers:
                    layer_data = layers[layer_name]
                    prompt_history = layer_data.get("prompt_history", [])
                    for hist_entry in prompt_history:
                        if hist_entry.get("version") == version_num:
                            prompt_details = hist_entry
                            break
                
                if success_rate < 0.3:  # Less than 30% success
                    message = f"{prompt_key}: {perf['high']}/{total} high-performers (success rate: {success_rate:.1%})"
                    recommendation = f"Prompt version performing poorly - consider revision for {layer_name} layer"
                    
                    if prompt_details:
                        reason = prompt_details.get("reason", "")
                        message += f" | Created: {reason}"
                        recommendation += f". Review the prompt created for: {reason}"
                    
                    analysis["insights"].append({
                        "type": "prompt_version_underperforming",
                        "message": message,
                        "recommendation": recommendation,
                        "prompt_version": version_num,
                        "layer": layer_name
                    })
                    
                elif success_rate > 0.7:  # More than 70% success
                    message = f"{prompt_key}: {perf['high']}/{total} high-performers (success rate: {success_rate:.1%})"
                    recommendation = f"This prompt version is effective - preserve its characteristics in future iterations"
                    
                    if prompt_details:
                        reason = prompt_details.get("reason", "")
                        message += f" | Created: {reason}"
                        recommendation += f". Key improvement was: {reason}"
                    
                    analysis["insights"].append({
                        "type": "prompt_version_effective",
                        "message": message,
                        "recommendation": recommendation,
                        "prompt_version": version_num,
                        "layer": layer_name
                    })
        
        return json.dumps(analysis, indent=2)
        
    except json.JSONDecodeError as e:
        return json.dumps({"valid": False, "error": f"Invalid JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"valid": False, "error": f"Error evaluating engagement: {str(e)}"})


# ===== WEAVE DATA FETCHING TOOL =====

def fetch_performance_data_from_weave(limit: int = 50) -> str:
    """
    Fetch recent performance data from Weave traces for analysis.
    
    This tool retrieves the latest agent execution data from Weave, including:
    - Recent agent calls and their success/failure status
    - Execution times and error information
    - Cost and feedback metrics
    
    Use this when you need current performance data to make decisions.
    
    Args:
        limit: Number of recent calls to fetch (default: 50)
    
    Returns:
        JSON string containing performance data with structure:
        {
            "iteration": 0,
            "layers": {
                "research": {"current_version": 1, "metrics": {}, "prompt_history": []},
                "creative_writer": {...},
                "generator": {...},
                "critic": {...},
                "safety": {...}
            },
            "overall_metrics": {
                "clarity": 0.85,
                "novelty": 0.75,
                ...
            },
            "content_history": []
        }
    """
    from hr_validation_agent.tools import get_calls_for_hr_validation
    
    # Get calls from Weave
    calls_data = get_calls_for_hr_validation(limit=limit)
    
    # Simple conversion to HR format
    agents_performance = calls_data.get("agents_performance", [])
    
    # Calculate success rate
    successful = sum(1 for p in agents_performance if p.get("success", False))
    total = len(agents_performance)
    success_rate = successful / total if total > 0 else 0
    
    print(f"[FETCH_TOOL] Retrieved {total} calls, success rate: {success_rate:.2%}")
    
    # Build layers with empty prompt history (bootstrap mode)
    layers = {}
    for layer_id in LAYER_DEFINITIONS.keys():
        layers[layer_id] = {
            "current_version": 1,
            "metrics": {},
            "prompt_history": []
        }
    
    # Build HR input
    hr_data = {
        "iteration": 0,
        "layers": layers,
        "overall_metrics": {
            "clarity": min(1.0, success_rate * 1.1),
            "novelty": min(1.0, success_rate * 0.9),
            "shareability": min(1.0, success_rate * 0.95),
            "credibility": min(1.0, success_rate * 1.05),
            "safety": min(1.0, success_rate * 1.2)
        },
        "content_history": []
    }
    
    return json.dumps(hr_data, indent=2)


# ===== ADK ROOT AGENT with Weave Tracking =====

# Step 1: Analyzer Agent
analyzer_agent = Agent(
    model='gemini-2.5-flash',
    name='analyzer',
    description='Analyzes layer performance metrics',
    instruction="""You are the Analyzer. MANDATORY WORKFLOW:

STEP 1: ALWAYS start by calling load_current_cmo_prompts()
   → This loads all current prompts from cmo_agent/sub_agents.py
   → You MUST do this first before any analysis

STEP 2: Check input format
   - If input is raw posts array (not full HR JSON):
     → Call create_hr_input_from_posts(recent_posts_json, iteration)
   - If input is already complete HR JSON:
     → Use it directly

STEP 3: Call analyze_layer_performance(complete_hr_json)
   → Pass the JSON string AS-IS from previous steps
   → DO NOT modify or reformat the JSON
   → Analyzes all layer metrics
   → Identifies improvements needed

STEP 4: Output the analysis results

CRITICAL RULES:
- MUST call load_current_cmo_prompts() first
- Pass JSON strings directly to functions WITHOUT modification
- Do NOT try to parse, edit, or reformat the JSON
- The JSON is already properly formatted and escaped""",
    tools=[
        analyze_layer_performance,
        create_hr_input_from_posts,
        load_current_cmo_prompts
    ]
)

# Step 2: Evaluator Agent
evaluator_agent = Agent(
    model='gemini-2.5-flash',
    name='evaluator',
    description='Evaluates content engagement if data exists',
    instruction="""You are the Evaluator. Call evaluate_content_engagement with the input JSON.

The tool will:
- Check if actual engagement data exists in the layers
- If yes: Analyze engagement patterns and return insights
- If no: Return "No content data provided"

Just call the tool with the complete input JSON string.""",
    tools=[evaluate_content_engagement]
)

# Step 3: Improver Agent (with structured output)
improver_agent = Agent(
    model='gemini-2.5-flash',
    name='improver',
    description='Creates and applies prompt improvements',
    instruction="""You are the Improver. Review the analysis and evaluation results from previous agents.

The analyzer provided performance metrics for each layer.
The evaluator provided engagement analysis (or "No content data" if unavailable).

Your task:
1. Identify layers with scores below thresholds
2. For each underperforming layer, create a COMPLETE improved system prompt
3. Call apply_prompt_improvements with the generated JSON

Generate a PromptOptimizationDecision JSON with:
- prompts: array of {layer, new_prompt, reason, expected_impact}
- thresholds: {clarity: 0.55, novelty: 0.55, shareability: 0.55, credibility: 0.60, safety: 0.80}
- global_adjustments: {target_audience_update, brand_voice, topics_to_avoid} (optional)

Each new_prompt MUST be a COMPLETE, SELF-CONTAINED system prompt (not just changes).

CRITICAL: When calling apply_prompt_improvements, pass the JSON as a properly formatted string.
Make sure all special characters in new_prompt are properly escaped for JSON.""",
    tools=[
        apply_prompt_improvements,
        list_cmo_versions,
        get_version_metadata,
        restore_cmo_version
    ]
)

# Sequential Agent: Runs analyzer → evaluator → improver in order
root_agent_sequential = SequentialAgent(
    name='hr_validation_pipeline',
    sub_agents=[analyzer_agent, evaluator_agent, improver_agent],
    description='Sequential HR validation: Analyze → Evaluate → Improve & Apply',
)

# Legacy single agent (for backward compatibility)
root_agent_legacy = Agent(
    model='gemini-2.5-flash',
    name='hr_validation_agent_legacy',
    description='Meta-agent that improves prompts for a 5-layer content creation system.',
    instruction="""You are PromptOptimizer — the meta-level manager for a 5-layer content creation system.

CRITICAL: You MUST respond with ONLY valid JSON. No text before or after the JSON object.

**WORKFLOW:**
1. **ALWAYS start by calling fetch_performance_data_from_weave()** to get current performance data
2. Use the returned data to analyze and make prompt improvement decisions
3. Optionally call analyze_layer_performance() or evaluate_content_engagement() for deeper analysis
4. Return your prompt improvement decisions as JSON

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

**Option 1: Direct user request (no input data)**
When the user simply asks you to improve the system, **call fetch_performance_data_from_weave()** first to get current data.

**Option 2: User provides explicit data**
You will receive a JSON with:
1. **layers** - Each layer contains:
   - `current_version`: Active prompt version number
   - `metrics`: Layer-specific performance metrics
   - `prompt_history`: Array of all prompt versions (with `is_active` flag)
2. **overall_metrics** - System-wide performance metrics
3. **content_history** - Recent content with actual performance data

**BOOTSTRAP MODE (iteration 0)**: If `prompt_history` is empty or no active prompts exist, you MUST create initial prompts for all 5 layers.

---

## AVAILABLE TOOLS

**fetch_performance_data_from_weave(limit)** — Fetch current performance data from Weave
- Input: limit (number of recent calls to fetch, default 50)
- Output: JSON with current system state including layers, metrics, and performance data
- **USE THIS FIRST** to get up-to-date performance information

**analyze_layer_performance(performance_json)** — Analyze metrics and identify weak layers
- Input: Performance data for all 5 layers
- Output: Analysis with layers needing improvement

**evaluate_content_engagement(content_engagement_json)** — Evaluate prompt-engagement correlations
- Input: Layer prompts + actual content with real engagement metrics
- Output: Pattern analysis showing which prompt characteristics lead to high engagement
- Use this when you have real-world engagement data (likes, retweets, shares, views)
- Identifies which layers contribute most to viral content
- Analyzes internal score dimensions that correlate with high engagement

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
- **Research layer** low → Improve data sources, trending topic identification, audience analysis depth
- **Creative Writer layer** low → Enhance creative constraints, add example formats, boost novelty techniques
- **Generator layer** low → Add clarity rules, structure templates, shareability patterns
- **Critic layer** low → Refine evaluation criteria, scoring rubrics, bias checks
- **Safety layer** low → Strengthen risk categories, compliance checks, brand guidelines

**IMPORTANT**: Always provide COMPLETE NEW PROMPTS, not modifications or patches.
Your output will directly replace the existing prompt, so ensure:
1. The new prompt is self-contained and complete
2. It preserves any working elements from the old prompt
3. It adds specific improvements based on performance data
4. It follows the layer's core responsibilities

---

## OUTPUT (STRICT JSON)

**BOOTSTRAP MODE (iteration 0 or no existing prompts):**

When creating initial prompts, design comprehensive system prompts for each layer:

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
  "prompts": [
    {
      "layer": "research",
      "new_prompt": "complete system prompt for this layer",
      "reason": "bootstrap - creating initial prompt",
      "expected_impact": "establish baseline behavior for research layer"
    },
    {
      "layer": "creative_writer",
      "new_prompt": "complete system prompt for this layer",
      "reason": "bootstrap - creating initial prompt",
      "expected_impact": "establish baseline behavior for creative writer layer"
    },
    {
      "layer": "generator",
      "new_prompt": "complete system prompt for this layer",
      "reason": "bootstrap - creating initial prompt",
      "expected_impact": "establish baseline behavior for generator layer"
    },
    {
      "layer": "critic",
      "new_prompt": "complete system prompt for this layer",
      "reason": "bootstrap - creating initial prompt",
      "expected_impact": "establish baseline behavior for critic layer"
    },
    {
      "layer": "safety",
      "new_prompt": "complete system prompt for this layer",
      "reason": "bootstrap - creating initial prompt",
      "expected_impact": "establish baseline behavior for safety layer"
    }
  ],
  "global_adjustments": {...},
  "thresholds": {...}
}

---

**IMPROVEMENT MODE (iteration > 0 with existing prompts):**

When improving existing prompts:
1. Analyze weak metrics from performance data
2. Review current prompt and identify what to preserve vs. improve
3. Generate COMPLETE NEW PROMPT that incorporates improvements
4. Maximum 3 layer improvements per iteration (focus on biggest issues)

Output structure:
{
  "prompts": [
    {
      "layer": "creative_writer",
      "new_prompt": "You are the Creative Writer layer. Your task is to generate creative, engaging, and novel content ideas for X (Twitter)...\n\n[COMPLETE FULL PROMPT HERE - this will REPLACE the old prompt entirely]",
      "reason": "shareability 0.48 < threshold 0.55; novelty 0.72 borderline; actual engagement 0%",
      "expected_impact": "increase shareability by 0.15+ through stronger hooks and emotional triggers; boost actual engagement rate to 2-5%"
    },
    {
      "layer": "generator",
      "new_prompt": "You are the Generator layer...\n\n[COMPLETE FULL PROMPT HERE]",
      "reason": "shareability 0.48 < threshold; 0% engagement despite good clarity",
      "expected_impact": "improve call-to-action strength and viral mechanics to drive engagement"
    }
  ],
  "global_adjustments": {...},
  "thresholds": {...}
}

---

## STYLE

- **RESPONSE FORMAT**: Output ONLY the JSON object. No markdown code blocks, no explanations, no commentary.
- Start your response directly with `{` and end with `}`
- Every prompt entry must include:
  * layer name (research/creative_writer/generator/critic/safety)
  * new_prompt (COMPLETE system prompt text that replaces the old one)
  * reason (specific metrics/issues identified)
  * expected impact (quantitative predictions where possible)
- **new_prompt must be COMPLETE and READY TO USE** — include all instructions, format specs, examples
- Be specific and actionable — no vague suggestions
- Limit to 3 layer improvements per iteration except bootstrap (5 layers)
- Always maintain safety layer as highest priority

---

## AUTO-APPLY TOOL

**Tool: apply_prompt_improvements** (formerly create_cmo_version_from_hr_output)
- Takes your JSON decisions and applies them to cmo_agent/sub_agents.py
- Backs up current version as cmo_agent_vX/
- Makes changes live for ADK to use immediately

Call this AFTER outputting your JSON decisions!

---

Remember: 
- **BOOTSTRAP (iteration 0)**: Output `prompts` with all 5 layers, each with complete `new_prompt`
- **IMPROVEMENTS (iteration > 0)**: Output `prompts` for 1-3 layers needing improvement, each with complete `new_prompt`
- OUTPUT ONLY JSON. No markdown, no text before/after.
- **USE evaluate_content_engagement** when real engagement data is available to identify prompt-performance patterns
- Each `new_prompt` should be a COMPLETE, SELF-CONTAINED system prompt (not a diff or modification)

**MANDATORY WORKFLOW (DO ALL STEPS IN ORDER):**

Step 1: Call analyze_layer_performance(input_json)
Step 2: If engagement data exists, call evaluate_content_engagement(engagement_data_json)
Step 3: Based on analysis, OUTPUT your JSON decisions (the prompts with new_prompt, reason, expected_impact)
Step 4: Call apply_prompt_improvements(hr_decisions_json=<your_json_from_step3_as_string>)
       → This updates cmo_agent/sub_agents.py automatically

IMPORTANT: Step 3 outputs JSON, Step 4 applies it to actual files. Do NOT skip Step 4!
""",
    tools=[
        analyze_layer_performance, 
        evaluate_content_engagement,
        apply_prompt_improvements,
        restore_cmo_version,
        list_cmo_versions,
        get_version_metadata
    ]
)

# Default to sequential agent
root_agent = root_agent_sequential
