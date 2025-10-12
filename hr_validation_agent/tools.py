"""
HR Validation Agent Tools
"""

import json
from typing import List, Dict, Any
import weave


def get_recent_calls_as_json(
    limit: int = 100,
    filter: dict = None,
    include_costs: bool = True,
    include_feedback: bool = True
) -> str:
    """
    Weave에서 최근 calls를 가져와서 JSON 형식으로 반환
    
    Args:
        limit: 가져올 call 개수
        filter: 필터 조건
        include_costs: 비용 정보 포함 여부
        include_feedback: 피드백 정보 포함 여부
    
    Returns:
        JSON string
    """
    # Use existing Weave client (initialized in agent.py via OTEL)
    import os
    client = weave.init(os.getenv("WANDB_PROJECT_ID", "mason-choi-storika/WeaveHacks2"))
    
    # Get calls with minimal columns (only output)
    calls_iter = client.get_calls(
        limit=limit,
        filter=filter,
        include_costs=include_costs,
        include_feedback=include_feedback,
        columns=["output"],  # Only fetch output column for performance
        sort_by=[{"field": "started_at", "direction": "desc"}]
    )
    
    calls = list(calls_iter)
    print(f"[HR_TOOLS] Found {len(calls)} calls")
    
    # Convert to JSON-serializable format
    calls_data = []
    for call in calls:
        call_dict = {
            "id": call.id,
            "trace_id": call.trace_id,
            "op_name": call.op_name,
            "started_at": call.started_at.isoformat() if call.started_at else None,
            "ended_at": call.ended_at.isoformat() if call.ended_at else None,
            "inputs": call.inputs if hasattr(call, 'inputs') else None,
            "output": call.output if hasattr(call, 'output') else None,
            "exception": call.exception if hasattr(call, 'exception') else None,
            "summary": call.summary if hasattr(call, 'summary') else None,
        }
        calls_data.append(call_dict)
    
    return json.dumps(calls_data, indent=2, default=str)


def get_calls_for_hr_validation(
    limit: int = 50,
    op_name_filter: str = None
) -> Dict[str, Any]:
    """
    HR Validation Agent용 input 형식으로 calls 데이터 변환
    
    Args:
        limit: 가져올 call 개수
        op_name_filter: 특정 operation만 필터링 (예: "CMOAgent.run")
    
    Returns:
        HR agent input 형식의 dict
    """
    # Use existing Weave client (initialized in agent.py via OTEL)
    import os
    client = weave.init(os.getenv("WANDB_PROJECT_ID", "mason-choi-storika/WeaveHacks2"))
    
    # Build filter
    filter_dict = None
    if op_name_filter:
        filter_dict = {"op_names": [op_name_filter]}
    
    # Get calls with minimal columns (only output)
    calls_iter = client.get_calls(
        limit=limit,
        filter=filter_dict,
        include_costs=True,
        include_feedback=True,
        columns=["output"],  # Only fetch output column for performance
        sort_by=[{"field": "started_at", "direction": "desc"}]
    )
    
    calls = list(calls_iter)
    print(f"[HR_TOOLS] Found {len(calls)} calls for HR validation")
    
    if calls:
        print(f"[HR_TOOLS] Sample call (entire object):")
        print(f"[HR_TOOLS] {calls[0]}")
        print(f"[HR_TOOLS] Type: {type(calls[0])}")
        print(f"[HR_TOOLS] Dir: {dir(calls[0])}")
    
    # Convert to HR agent format
    agents_performance = []
    
    for call in calls:
        # Extract performance metrics from call
        agent_data = {
            "agent_name": call.op_name,
            "call_id": call.id,
            "execution_time_ms": None,
            "success": call.exception is None,
            "metrics": {}
        }
        
        # Calculate execution time
        if call.started_at and call.ended_at:
            duration = (call.ended_at - call.started_at).total_seconds() * 1000
            agent_data["execution_time_ms"] = duration
        
        # Extract metrics from summary
        if hasattr(call, 'summary') and call.summary:
            summary = call.summary
            if isinstance(summary, dict):
                # Extract Weave metrics
                if 'weave' in summary:
                    weave_data = summary['weave']
                    if 'costs' in weave_data:
                        agent_data["metrics"]["costs"] = weave_data['costs']
                    if 'feedback' in weave_data:
                        agent_data["metrics"]["feedback"] = weave_data['feedback']
        
        agents_performance.append(agent_data)
    
    return {
        "iteration": 0,  # 필요시 파라미터로 받기
        "agents_performance": agents_performance,
        "total_calls": len(calls),
        "timestamp": calls[0].started_at.isoformat() if calls and calls[0].started_at else None
    }


# Test code (comment out in production)
if __name__ == "__main__":
    # Test 1: Get as JSON
    print("=" * 70)
    print("Test 1: Get calls as JSON")
    print("=" * 70)
    json_data = get_recent_calls_as_json(limit=5)
    print(json_data[:500] + "...")
    
    print("\n" + "=" * 70)
    print("Test 2: Get for HR validation")
    print("=" * 70)
    hr_input = get_calls_for_hr_validation(limit=10)
    print(json.dumps(hr_input, indent=2, default=str)[:800] + "...")