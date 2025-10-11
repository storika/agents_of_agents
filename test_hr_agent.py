"""
Pytest-style tests for HR Validation Agent.
"""

import json
from pathlib import Path
from hr_validation_agent import root_agent
from hr_validation_agent.schemas import TeamState


def test_hr_agent_basic():
    """Test basic functionality with JSON input/output."""
    with open("examples/team_state.sample.json") as f:
        team_state = json.load(f)
    
    # Convert to JSON string for the tool
    team_state_json = json.dumps(team_state)
    
    # Call the agent's tool directly
    from hr_validation_agent.agent import analyze_team_and_decide
    result_json = analyze_team_and_decide(team_state_json)
    
    # Parse result
    decisions = json.loads(result_json)
    
    # Schema validation
    assert "hire_plan" in decisions
    assert "merge_plan" in decisions
    assert "prune_list" in decisions
    assert "prompt_feedback" in decisions
    assert "policies" in decisions
    
    # Type validation
    assert isinstance(decisions["hire_plan"], list)
    assert isinstance(decisions["merge_plan"], list)
    assert isinstance(decisions["prune_list"], list)
    assert isinstance(decisions["prompt_feedback"], list)
    assert isinstance(decisions["policies"], dict)
    
    # Policy validation
    assert decisions["policies"]["team_cap"] == 8
    assert decisions["policies"]["utility_floor"] == 0.35


def test_deterministic_behavior():
    """Test that same input produces same output."""
    with open("examples/team_state.sample.json") as f:
        team_state = json.load(f)
    
    team_state_json = json.dumps(team_state)
    
    from hr_validation_agent.agent import analyze_team_and_decide
    
    d1 = json.loads(analyze_team_and_decide(team_state_json))
    d2 = json.loads(analyze_team_and_decide(team_state_json))
    
    assert d1 == d2, "Same seed should produce identical decisions"


def test_sample_state_decisions():
    """Test expected decisions for sample state."""
    with open("examples/team_state.sample.json") as f:
        team_state = json.load(f)
    
    team_state_json = json.dumps(team_state)
    
    from hr_validation_agent.agent import analyze_team_and_decide
    decisions = json.loads(analyze_team_and_decide(team_state_json))
    
    # Expected: novelty is low (0.52 < 0.55), should hire specialist
    assert len(decisions["hire_plan"]) > 0, "Should hire specialist for low novelty"
    
    # Expected: DullWriter has utility 0.28 < 0.35, should be pruned
    prune_names = [p["name"] for p in decisions["prune_list"]]
    assert "DullWriter" in prune_names, "DullWriter should be pruned (low utility)"
    
    # Expected: DullWriter and Explainer have high similarity (0.85)
    merge_pairs = [(m["a"], m["b"]) for m in decisions["merge_plan"]]
    has_dull_explainer_merge = any(
        ("DullWriter" in pair and "Explainer" in pair) for pair in merge_pairs
    )
    assert has_dull_explainer_merge, "Should suggest merging similar agents"
    
    # Expected: DullWriter significantly underperforms (0.48 vs mean 0.70), should get feedback
    feedback_agents = [f["agent"] for f in decisions["prompt_feedback"]]
    assert "DullWriter" in feedback_agents, "DullWriter should receive coaching (score 0.48 << mean 0.70)"


def test_json_error_handling():
    """Test that invalid JSON is handled gracefully."""
    from hr_validation_agent.agent import analyze_team_and_decide
    
    # Invalid JSON
    result = analyze_team_and_decide("not valid json")
    parsed = json.loads(result)
    assert "error" in parsed
    
    # Valid JSON but invalid schema
    result = analyze_team_and_decide('{"invalid": "schema"}')
    parsed = json.loads(result)
    assert "error" in parsed


def test_empty_team_bootstrap():
    """Test that empty team triggers initial team creation via LLM."""
    from hr_validation_agent.agent import analyze_team_and_decide
    
    with open("examples/empty_team.json") as f:
        empty_team = json.load(f)
    
    result = analyze_team_and_decide(json.dumps(empty_team))
    decisions = json.loads(result)
    
    # Should create initial team (LLM decides size, typically 3-5)
    assert len(decisions["hire_plan"]) >= 3, "Should hire at least 3 initial team members"
    assert len(decisions["hire_plan"]) <= 5, "Should hire at most 5 initial team members"
    
    # Should have at least one writer and one critic
    hire_roles = [h["role"] for h in decisions["hire_plan"]]
    assert any("writer" in role for role in hire_roles), "Should have at least one writer"
    assert any("critic" in role for role in hire_roles), "Should have at least one critic"
    
    # Check reasons mention bootstrap
    for hire in decisions["hire_plan"]:
        assert "Bootstrap" in hire["reason"], "Reason should mention bootstrap"
        assert len(hire["system_prompt"]) > 50, "System prompt should be substantial"


if __name__ == "__main__":
    # Run all tests
    test_hr_agent_basic()
    print("✅ test_hr_agent_basic passed")
    
    test_deterministic_behavior()
    print("✅ test_deterministic_behavior passed")
    
    test_sample_state_decisions()
    print("✅ test_sample_state_decisions passed")
    
    test_json_error_handling()
    print("✅ test_json_error_handling passed")
    
    test_empty_team_bootstrap()
    print("✅ test_empty_team_bootstrap passed")
    
    print("\n🎉 All tests passed!")
