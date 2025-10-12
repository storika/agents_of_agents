"""
HR Validation Agent - Prompt Loader Tools
Automatically load current CMO agent prompts for validation
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional


def load_current_cmo_prompts() -> str:
    """
    Load current CMO agent prompts from sub_agents.py
    
    Returns:
        JSON string with current prompts and default metrics structure
    """
    try:
        workspace_path = Path(__file__).parent.parent
        sub_agents_path = workspace_path / "cmo_agent" / "sub_agents.py"
        
        if not sub_agents_path.exists():
            return json.dumps({
                "error": "sub_agents.py not found",
                "path": str(sub_agents_path)
            })
        
        # Read file
        with open(sub_agents_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract prompts for each layer
        layers = {}
        
        # Layer definitions
        layer_functions = {
            "research": "create_research_agent",
            "creative_writer": "create_creative_writer_agent",
            "generator": "create_generator_agent",
            "critic": "create_critic_agent",
            "safety": "create_safety_agent"
        }
        
        for layer_name, func_name in layer_functions.items():
            # Extract system_prompt from function
            pattern = rf'def {func_name}\(\).*?system_prompt = """(.*?)"""'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                # Extract prompt and ensure it's properly formatted
                prompt = match.group(1).strip()
                
                # Default metrics based on layer type
                if layer_name == "research":
                    metrics = {
                        "relevance": 0.70,
                        "timeliness": 0.65,
                        "data_quality": 0.75
                    }
                elif layer_name == "creative_writer":
                    metrics = {
                        "novelty": 0.70,
                        "creativity": 0.68,
                        "engagement_potential": 0.60
                    }
                elif layer_name == "generator":
                    metrics = {
                        "clarity": 0.75,
                        "shareability": 0.55,
                        "completeness": 0.80
                    }
                elif layer_name == "critic":
                    metrics = {
                        "accuracy": 0.80,
                        "thoroughness": 0.75,
                        "constructiveness": 0.70
                    }
                elif layer_name == "safety":
                    metrics = {
                        "safety_score": 0.95,
                        "compliance": 0.90,
                        "risk_detection": 0.85
                    }
                
                layers[layer_name] = {
                    "current_version": 1,
                    "metrics": metrics,
                    "prompt_history": [
                        {
                            "version": 1,
                            "prompt": prompt,
                            "created_at": "2025-10-12T00:00:00Z",
                            "reason": "Current active prompt",
                            "is_active": True
                        }
                    ]
                }
        
        # Create HR input structure
        hr_input = {
            "iteration": 0,
            "layers": layers,
            "thresholds": {
                "clarity": 0.55,
                "novelty": 0.55,
                "shareability": 0.55,
                "credibility": 0.60,
                "safety": 0.80
            }
        }
        
        # Use json.dumps to properly escape all strings
        return json.dumps(hr_input, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "error_type": type(e).__name__
        })


def create_hr_input_from_posts(
    recent_posts_json: str = "[]",
    iteration: int = 1
) -> str:
    """
    Create complete HR validation input from current prompts + recent post performance
    
    Args:
        recent_posts_json: JSON string with recent posts and their performance
            Format: [
                {
                    "content_id": "post_123",
                    "contributors": ["research", "creative_writer", "generator"],
                    "internal_scores": {"clarity": 0.8, "novelty": 0.7, ...},
                    "actual_performance": {"impressions": 5000, "likes": 120, ...}
                },
                ...
            ]
        iteration: Current iteration number
    
    Returns:
        JSON string ready for HR validation agent
    
    Example:
        >>> posts = [{"content_id": "post_1", "contributors": ["research"], ...}]
        >>> hr_input = create_hr_input_from_posts(json.dumps(posts), iteration=1)
        >>> # Use with HR agent
    """
    # Apply default values (Google AI doesn't support default values in function declarations)
    if recent_posts_json is None:
        recent_posts_json = "[]"
    if iteration is None:
        iteration = 1
    
    try:
        # Load current prompts
        current_prompts = json.loads(load_current_cmo_prompts())
        
        if "error" in current_prompts:
            return json.dumps(current_prompts)
        
        # Parse recent posts
        recent_posts = json.loads(recent_posts_json)
        
        # Calculate aggregate metrics per layer
        layer_metrics = {}
        for layer_name in current_prompts["layers"].keys():
            layer_metrics[layer_name] = {
                "total_contributions": 0,
                "avg_internal_scores": {},
                "avg_performance": {}
            }
        
        # Aggregate metrics from posts
        for post in recent_posts:
            contributors = post.get("contributors", [])
            internal_scores = post.get("internal_scores", {})
            actual_performance = post.get("actual_performance", {})
            
            for contributor in contributors:
                if contributor in layer_metrics:
                    layer_metrics[contributor]["total_contributions"] += 1
                    
                    # Average internal scores
                    for metric, value in internal_scores.items():
                        if metric not in layer_metrics[contributor]["avg_internal_scores"]:
                            layer_metrics[contributor]["avg_internal_scores"][metric] = []
                        layer_metrics[contributor]["avg_internal_scores"][metric].append(value)
                    
                    # Average performance
                    for metric, value in actual_performance.items():
                        if metric not in layer_metrics[contributor]["avg_performance"]:
                            layer_metrics[contributor]["avg_performance"][metric] = []
                        if isinstance(value, (int, float)):
                            layer_metrics[contributor]["avg_performance"][metric].append(value)
        
        # Update metrics with actual data
        for layer_name, data in layer_metrics.items():
            if data["total_contributions"] > 0:
                # Average internal scores
                for metric, values in data["avg_internal_scores"].items():
                    if values:
                        avg = sum(values) / len(values)
                        current_prompts["layers"][layer_name]["metrics"][metric] = round(avg, 2)
                
                # Add actual engagement data
                current_prompts["layers"][layer_name]["actual_engagement"] = {
                    "content": recent_posts  # Full posts for detailed analysis
                }
        
        # Update iteration
        current_prompts["iteration"] = iteration
        
        # Use json.dumps to properly escape all strings including prompts
        return json.dumps(current_prompts, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "error_type": type(e).__name__
        })


# Example usage
if __name__ == "__main__":
    # Test loading current prompts
    print("Loading current CMO prompts...")
    result = load_current_cmo_prompts()
    data = json.loads(result)
    
    if "error" not in data:
        print(f"✅ Loaded {len(data['layers'])} layers")
        for layer_name in data['layers'].keys():
            print(f"  - {layer_name}")
    else:
        print(f"❌ Error: {data['error']}")
    
    # Test creating HR input from posts
    print("\nCreating HR input from sample posts...")
    sample_posts = [
        {
            "content_id": "post_1",
            "contributors": ["research", "creative_writer", "generator"],
            "internal_scores": {
                "clarity": 0.75,
                "novelty": 0.68,
                "shareability": 0.50
            },
            "actual_performance": {
                "impressions": 5000,
                "likes": 120,
                "retweets": 25,
                "engagement_rate": 0.029
            }
        }
    ]
    
    hr_input = create_hr_input_from_posts(json.dumps(sample_posts), iteration=1)
    hr_data = json.loads(hr_input)
    
    if "error" not in hr_data:
        print(f"✅ Created HR input for iteration {hr_data['iteration']}")
    else:
        print(f"❌ Error: {hr_data['error']}")

