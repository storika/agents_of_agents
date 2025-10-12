"""
HR Validation Agent - ADK Standard Implementation with Weave Integration
Focuses on improving prompts for 5 fixed layers: Research, Creative Writer, Generator, Critic, Safety
"""

import json
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===== OpenTelemetry Configuration for Weave =====
# Reference: https://google.github.io/adk-docs/observability/weave/#sending-traces-to-weave

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace

# Configure Weave endpoint and authentication
WANDB_BASE_URL = "https://trace.wandb.ai"
# PROJECT_ID = os.environ.get("mason-choi-storika/otel-hr")
PROJECT_ID = "mason-choi-storika/otel-hr"
OTEL_EXPORTER_OTLP_ENDPOINT = f"{WANDB_BASE_URL}/otel/v1/traces"

# Set up authentication
os.environ['WANDB_API_KEY'] = '3875d64c87801e9a71318a5a8754a0ee2d556946'
WANDB_API_KEY = os.environ['WANDB_API_KEY']
AUTH = base64.b64encode(f"api:{WANDB_API_KEY}".encode()).decode()

OTEL_EXPORTER_OTLP_HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "project_id": PROJECT_ID,
}

# Create the OTLP span exporter with endpoint and headers
exporter = OTLPSpanExporter(
    endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
    headers=OTEL_EXPORTER_OTLP_HEADERS,
)

# Get the current tracer provider (or create new if none exists)
current_tracer_provider = trace.get_tracer_provider()

# Check if it's a real TracerProvider or just the default proxy
if isinstance(current_tracer_provider, trace_sdk.TracerProvider):
    # TracerProvider already exists, add our exporter to it
    tracer_provider = current_tracer_provider
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    print(f"[INFO] 🐝 OpenTelemetry: Added Weave exporter to existing TracerProvider for {PROJECT_ID}")
else:
    # No TracerProvider yet, create a new one
    tracer_provider = trace_sdk.TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)
    print(f"[INFO] 🐝 OpenTelemetry: Created new TracerProvider for Weave: {PROJECT_ID}")

# Now import ADK (AFTER setting up tracer provider)
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

# Import tools
from hr_validation_agent.tools import measure_tweet_engagement, get_calls_for_hr_validation


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
        # Try parsing JSON with fallback (same as analyze_layer_performance)
        try:
            data = json.loads(content_engagement_json)
        except json.JSONDecodeError as parse_error:
            print(f"⚠️ [EVALUATE] Direct parse failed: {str(parse_error)[:100]}")
            try:
                from json_repair import repair_json
                repaired = repair_json(content_engagement_json)
                data = json.loads(repaired)
                print("✅ [EVALUATE] json-repair successful")
            except ImportError:
                print("ℹ️ [EVALUATE] json-repair not available, skipping evaluation")
                return json.dumps({
                    "valid": False,
                    "error": "JSON parsing failed and json-repair not available",
                    "suggestion": "Check JSON format or install json-repair library"
                })
            except Exception as repair_error:
                print(f"❌ [EVALUATE] json-repair failed: {str(repair_error)[:100]}")
                return json.dumps({
                    "valid": False,
                    "error": "JSON parsing failed",
                    "original_error": str(parse_error)[:200]
                })
        
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
    # Get calls from Weave
    calls_data = get_calls_for_hr_validation(limit=limit, op_name_filter="execute_tool call_post_agent")
    
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

# Step 1: Analyzer Agent (Sequential - 4 sub-steps)

# Sub-step 1.0: Fetch performance data from Weave
fetch_weave_data_agent = Agent(
    model='gemini-2.5-flash',
    name='fetch_weave_data',
    description='Fetches recent call data from Weave',
    instruction="""You MUST call get_calls_for_hr_validation() function NOW!

CRITICAL: DO NOT just explain. ACTUALLY CALL THE FUNCTION!

This function fetches recent performance data from Weave.
Call it with:

get_calls_for_hr_validation(limit=50, op_name_filter=None)

Or just:
get_calls_for_hr_validation()

DO IT NOW!""",
    tools=[get_calls_for_hr_validation]
)

# Sub-step 1.1: Load current prompts
load_prompts_agent = Agent(
    model='gemini-2.5-flash',
    name='load_prompts',
    description='Loads current CMO prompts',
    instruction="""You MUST call load_current_cmo_prompts() function NOW!

CRITICAL: DO NOT just explain. ACTUALLY CALL THE FUNCTION!

This function loads current prompts from cmo_agent/sub_agents.py.
It takes no arguments - just call it:

load_current_cmo_prompts()

DO IT NOW!""",
    tools=[load_current_cmo_prompts]
)

# Sub-step 1.2: Create HR input from posts
create_hr_input_agent = Agent(
    model='gemini-2.5-flash',
    name='create_hr_input',
    description='Creates HR input JSON from user posts',
    instruction="""You MUST call create_hr_input_from_posts() function now!

CRITICAL: DO NOT just explain or give examples. ACTUALLY CALL THE FUNCTION!

The function takes:
1. recent_posts_json: The original user input (JSON string with posts data)
2. iteration: Set to 1

Example call:
create_hr_input_from_posts(
    recent_posts_json='[{"content_id": "...", "internal_scores": {...}, ...}]',
    iteration=1
)

The user input from the sequential workflow will be available to you.
Use that exact input and pass it to the function.

DO IT NOW - call the function and return its result!""",
    tools=[create_hr_input_from_posts]
)

# Sub-step 1.3: Analyze layer performance
analyze_performance_agent = Agent(
    model='gemini-2.5-flash',
    name='analyze_performance',
    description='Analyzes layer performance metrics',
    instruction="""You MUST call analyze_layer_performance() function NOW!

CRITICAL: DO NOT just explain. ACTUALLY CALL THE FUNCTION!

The function takes one argument:
- performance_json: The complete HR JSON from the previous step (you received this from create_hr_input_agent)

Example call:
analyze_layer_performance(performance_json='{"iteration": 1, "layers": {...}, ...}')

Use the JSON output from the previous agent and pass it to this function.

DO IT NOW!""",
    tools=[analyze_layer_performance]
)

# Combine into sequential analyzer
analyzer_agent = SequentialAgent(
    name='analyzer_sequential',
    sub_agents=[fetch_weave_data_agent, load_prompts_agent, create_hr_input_agent, analyze_performance_agent],
    description='Sequential analyzer: Fetch Weave data → Load prompts → Create HR input → Analyze performance'
)

# Step 2: Evaluator Agent
evaluator_agent = Agent(
    model='gemini-2.5-flash',
    name='evaluator',
    description='Evaluates content engagement if data exists',
    instruction="""You MUST call evaluate_content_engagement() function NOW!

CRITICAL: DO NOT just explain. ACTUALLY CALL THE FUNCTION!

The function takes:
- content_engagement_json: The input from previous steps (passed automatically in sequential workflow)

Call it like this:
evaluate_content_engagement(content_engagement_json='...')

The tool will:
- Check if actual engagement data exists
- If yes: Return engagement analysis
- If no or if parsing fails: Return error (that's OK, workflow continues)

DO IT NOW - call the function!""",
    tools=[evaluate_content_engagement]
)

# Step 3: Improver Agent (with structured output)
improver_agent = Agent(
    model='gemini-2.5-flash',
    name='improver',
    description='Creates and applies prompt improvements',
    instruction="""You MUST create improvement JSON and call apply_prompt_improvements() function!

WORKFLOW:
1. Review analysis results from previous agents (analyzer + evaluator)
2. Generate a PromptOptimizationDecision JSON
3. Call apply_prompt_improvements() with that JSON

JSON FORMAT (you must create this):
{
  "prompts": [
    {
      "layer": "research" or "creative_writer" or "generator" or "critic" or "safety",
      "new_prompt": "COMPLETE full system prompt text here (not just changes!)",
      "reason": "specific metrics/issues identified",
      "expected_impact": "quantitative predictions"
    }
  ],
  "thresholds": {
    "clarity": 0.55,
    "novelty": 0.55,
    "shareability": 0.55,
    "credibility": 0.60,
    "safety": 0.80
  },
  "global_adjustments": {}
}

THEN CALL:
apply_prompt_improvements(hr_decisions_json='<your JSON as string>')

CRITICAL RULES:
- Each new_prompt MUST be COMPLETE (not just changes)
- Properly escape all special characters (\\n for newlines, \\" for quotes)
- Actually CALL apply_prompt_improvements() function - don't just output JSON!
- Focus on layers with scores below thresholds

DO IT NOW!""",
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

# Default to sequential agent (analyze → evaluate → improve)
root_agent = root_agent_sequential
