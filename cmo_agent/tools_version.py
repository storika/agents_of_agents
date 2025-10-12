"""
CMO Agent 버전 관리 Tools - ADK Agent에서 직접 사용 가능
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from cmo_agent.version_updater import CMOVersionUpdater


def apply_prompt_improvements(
    hr_decisions_json: str,
    version_name: Optional[str] = None,
    backup_current: bool = True
) -> str:
    """
    HR Agent의 프롬프트 개선 결정을 CMO Agent에 실제 적용
    
    이 tool은 HR Agent가 출력한 JSON 결정을 받아서 cmo_agent/sub_agents.py를 
    직접 수정합니다. 이전 버전은 자동으로 백업됩니다.
    
    Args:
        hr_decisions_json: HR Agent가 출력한 결정 JSON 문자열
            {
              "prompts": [
                {
                  "layer": "research|creative_writer|generator|...",
                  "new_prompt": "새로운 system prompt",
                  "reason": "변경 이유",
                  "expected_impact": "예상 효과"
                }
              ],
              "thresholds": {...}
            }
        version_name: 버전 이름 (선택사항, None이면 타임스탬프 자동 생성)
        backup_current: 현재 버전을 백업할지 여부 (기본값: True)
    
    Returns:
        JSON 문자열로 결과 반환:
        {
          "status": "success|failed",
          "version_name": "버전 이름",
          "applied_to_main": true,
          "updated_layers": ["layer1", "layer2", ...],
          "changes_summary": [...],
          "backup_path": "백업 경로"
        }
    
    Example:
        >>> # HR Agent가 JSON을 출력한 후
        >>> result_json = apply_prompt_improvements(
        ...     hr_decisions_json=json.dumps(hr_output),
        ...     version_name="v1.0_viral_optimized"
        ... )
        >>> result = json.loads(result_json)
        >>> print(f"CMO Agent 업데이트 완료: {result['version_name']}")
    """
    try:
        # JSON 파싱 (robust 처리)
        import re
        import ast
        
        # 1. 마크다운 코드 블록 제거
        cleaned = hr_decisions_json
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        
        # 2. JSON 객체만 추출 (앞뒤 텍스트 제거)
        if "{" in cleaned and "}" in cleaned:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            cleaned = cleaned[start:end]
        
        # 3. 파싱 시도 - 여러 방법 시도
        hr_output = None
        last_error = None
        
        # 방법 1: 직접 파싱 (가장 빠름)
        try:
            hr_output = json.loads(cleaned)
        except json.JSONDecodeError as e:
            last_error = e
            
            # 방법 2: ast.literal_eval로 Python dict로 파싱 후 재변환
            try:
                # 작은따옴표를 큰따옴표로 변환
                cleaned_py = cleaned.replace("'", '"')
                hr_output = json.loads(cleaned_py)
            except Exception as e2:
                # 방법 3: Pydantic으로 파싱 시도
                try:
                    from hr_validation_agent.schemas import PromptOptimizationDecision
                    hr_output = PromptOptimizationDecision.model_validate_json(cleaned).model_dump()
                except Exception as e3:
                    # 모든 방법 실패
                    raise last_error
        
        if hr_output is None:
            raise ValueError("Failed to parse JSON after all attempts")
        
        # 버전 업데이터 생성
        updater = CMOVersionUpdater()
        
        print(f"\n🤖 [Tool] CMO Agent 업데이트 시작...")
        
        # cmo_agent/에 직접 적용 (apply_directly=True)
        result = updater.create_new_version(
            hr_output=hr_output,
            version_name=version_name,
            backup_current=backup_current,
            apply_directly=True  # 직접 적용!
        )
        
        if result["status"] == "success":
            print(f"✅ [Tool] CMO Agent 업데이트 완료: {result['version_name']}")
            print(f"🎯 cmo_agent/sub_agents.py가 즉시 사용 가능합니다!")
        else:
            print(f"❌ [Tool] 업데이트 실패")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except json.JSONDecodeError as e:
        error_result = {
            "status": "failed",
            "error": str(e),
            "error_type": "JSONDecodeError",
            "json_preview": hr_decisions_json[:500] + "..." if len(hr_decisions_json) > 500 else hr_decisions_json
        }
        print(f"❌ [Tool] JSON 파싱 실패: {e}")
        print(f"📝 JSON 미리보기:\n{hr_decisions_json[:500]}...")
        return json.dumps(error_result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        error_result = {
            "status": "failed",
            "error": str(e),
            "error_type": type(e).__name__
        }
        print(f"❌ [Tool] 업데이트 실패: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps(error_result, ensure_ascii=False, indent=2)


# Backward compatibility alias
create_cmo_version_from_hr_output = apply_prompt_improvements


def restore_cmo_version(
    version_dir_name: str
) -> str:
    """
    이전 버전으로 복원 (cmo_agent_vX → cmo_agent/)
    
    Args:
        version_dir_name: 복원할 버전 디렉토리 이름 (예: "cmo_agent_v1" 또는 "cmo_agent_v0")
    
    Returns:
        JSON 문자열로 결과 반환
    """
    try:
        updater = CMOVersionUpdater()
        
        print(f"\n🔄 [Tool] 버전 복원: {version_dir_name}")
        
        result = updater.restore_version(version_dir_name, backup_current=True)
        
        if result["status"] == "success":
            print(f"✅ [Tool] 복원 완료: {version_dir_name}")
        else:
            print(f"❌ [Tool] 복원 실패: {result.get('error')}")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    except Exception as e:
        error_result = {
            "status": "failed",
            "error": str(e)
        }
        print(f"❌ [Tool] 복원 실패: {e}")
        return json.dumps(error_result, ensure_ascii=False, indent=2)


def list_cmo_versions() -> str:
    """
    생성된 모든 CMO Agent 버전 목록 조회 (cmo_agent_vX 형식)
    
    Returns:
        JSON 문자열로 버전 목록 반환:
        [
          {
            "directory": "cmo_agent_v1",
            "path": "/path/to/cmo_agent_v1",
            "version_name": "v1.0",
            "created_at": "2025-10-12T15:30:00",
            "updated_layers": ["research", "creative_writer"],
            "changes": [...]
          },
          ...
        ]
    """
    try:
        updater = CMOVersionUpdater()
        versions = updater.list_versions()
        
        print(f"\n📋 [Tool] 총 {len(versions)}개 버전 발견")
        for v in versions:
            print(f"   - {v.get('directory', 'unknown')}: {v.get('version_name', 'N/A')}")
        
        return json.dumps(versions, ensure_ascii=False, indent=2)
    
    except Exception as e:
        error_result = {
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)




def get_version_metadata(version_dir_name: str) -> str:
    """
    특정 버전의 메타데이터 조회
    
    Args:
        version_dir_name: 버전 디렉토리 이름 (예: "cmo_agent_v1")
    
    Returns:
        JSON 문자열로 메타데이터 반환
    """
    try:
        updater = CMOVersionUpdater()
        version_path = updater.workspace_path / version_dir_name
        metadata_path = version_path / "version_metadata.json"
        
        if not metadata_path.exists():
            return json.dumps({
                "error": f"Version not found: {version_dir_name}"
            })
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"\n📊 [Tool] 메타데이터 조회: {version_dir_name}")
        
        return json.dumps(metadata, ensure_ascii=False, indent=2)
    
    except Exception as e:
        error_result = {
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

