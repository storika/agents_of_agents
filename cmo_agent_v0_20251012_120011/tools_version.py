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
    def repair_json(text: str) -> str:
        """Repair malformed JSON by fixing common issues"""
        import re
        
        # 1. 문자열 내부의 unescaped newlines/tabs/quotes 수정
        def fix_string_content(match):
            content = match.group(1)
            # Escape special characters
            content = content.replace('\n', '\\n')
            content = content.replace('\r', '\\r')
            content = content.replace('\t', '\\t')
            content = content.replace('\b', '\\b')
            content = content.replace('\f', '\\f')
            # Fix already escaped sequences (avoid double escaping)
            content = content.replace('\\\\n', '\\n')
            content = content.replace('\\\\r', '\\r')
            content = content.replace('\\\\t', '\\t')
            return f'"{content}"'
        
        # Find all string values (between quotes)
        repaired = re.sub(r'"([^"]*)"', fix_string_content, text)
        
        # 2. Remove trailing commas before } or ]
        repaired = re.sub(r',\s*([}\]])', r'\1', repaired)
        
        # 3. Fix single quotes to double quotes (for keys and string values)
        # But be careful not to mess with already fixed strings
        repaired = re.sub(r"(\w+)'s", r'\1\\\'s', repaired)  # Protect possessives
        
        return repaired
    
    try:
        # JSON 파싱 (ultra-robust with json-repair library)
        import re
        from json_repair import repair_json as json_repair_lib
        
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
        
        # 3. Multiple parsing strategies (with optional json-repair)
        hr_output = None
        last_error = None
        
        # Check if json-repair is available
        try:
            from json_repair import repair_json as json_repair_lib
            HAS_JSON_REPAIR = True
        except ImportError:
            HAS_JSON_REPAIR = False
            print("ℹ️ [JSON] json-repair library not available, using custom repair only")
        
        # Strategy 1: Direct parsing (fastest)
        try:
            hr_output = json.loads(cleaned)
            print("✅ [JSON] Direct parsing successful")
        except json.JSONDecodeError as e:
            last_error = e
            print(f"⚠️ [JSON] Direct parsing failed: {str(e)[:100]}")
            
            # Strategy 2: json-repair library (if available)
            if HAS_JSON_REPAIR:
                try:
                    repaired = json_repair_lib(cleaned)
                    hr_output = json.loads(repaired)
                    print("✅ [JSON] json-repair library successful")
                except Exception as e2:
                    print(f"⚠️ [JSON] json-repair failed: {str(e2)[:100]}")
            
            # Strategy 3: Custom repair
            if hr_output is None:
                try:
                    custom_repaired = repair_json(cleaned)
                    hr_output = json.loads(custom_repaired)
                    print("✅ [JSON] Custom repair successful")
                except Exception as e3:
                    print(f"⚠️ [JSON] Custom repair failed: {str(e3)[:100]}")
                    
                    # Strategy 4: Custom + json-repair combo (if available)
                    if HAS_JSON_REPAIR:
                        try:
                            double_repaired = json_repair_lib(custom_repaired)
                            hr_output = json.loads(double_repaired)
                            print("✅ [JSON] Double repair successful")
                        except Exception as e4:
                            print(f"⚠️ [JSON] Double repair failed: {str(e4)[:100]}")
                    
                    # Strategy 5: Pydantic validation (last resort)
                    if hr_output is None:
                        try:
                            from hr_validation_agent.schemas import PromptOptimizationDecision
                            # Try with best available repaired version
                            repaired_for_pydantic = double_repaired if HAS_JSON_REPAIR and 'double_repaired' in locals() else custom_repaired
                            hr_output = PromptOptimizationDecision.model_validate_json(repaired_for_pydantic).model_dump()
                            print("✅ [JSON] Pydantic validation successful")
                        except Exception as e5:
                            print(f"⚠️ [JSON] Pydantic failed: {str(e5)[:100]}")
                            # All methods failed
                            if last_error:
                                raise last_error
                            else:
                                raise ValueError("Failed to parse JSON after all repair attempts")
        
        if hr_output is None:
            raise ValueError("Failed to parse JSON after all repair attempts")
        
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

