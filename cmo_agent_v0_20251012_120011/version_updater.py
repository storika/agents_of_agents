"""
CMO Agent Version Updater Tool
HR Validation Agent의 프롬프트 개선 결과를 기반으로 새로운 버전의 CMO Agent를 생성하는 도구
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import shutil


class CMOVersionUpdater:
    """CMO Agent의 새로운 버전을 생성하고 관리하는 클래스"""
    
    def __init__(self, workspace_path: str = None):
        """
        Args:
            workspace_path: 워크스페이스 경로 (기본값: 현재 파일 위치 기준)
        """
        if workspace_path is None:
            self.workspace_path = Path(__file__).parent.parent
        else:
            self.workspace_path = Path(workspace_path)
        
        self.cmo_agent_dir = self.workspace_path / "cmo_agent"
    
    def create_new_version(
        self, 
        hr_output: Dict[str, Any],
        version_name: str = None,
        backup_current: bool = True,
        apply_directly: bool = True
    ) -> Dict[str, Any]:
        """
        HR Agent의 출력을 기반으로 새로운 버전의 CMO Agent 생성
        
        Args:
            hr_output: HR Validation Agent의 출력 JSON
                {
                  "prompts": [
                    {
                      "layer": "research|creative_writer|generator|...",
                      "new_prompt": "새로운 system prompt",
                      "reason": "변경 이유",
                      "expected_impact": "예상 효과"
                    }
                  ],
                  "thresholds": {...},
                  "global_adjustments": {...}
                }
            version_name: 버전 이름 (기본값: 타임스탬프)
            backup_current: 현재 버전 백업 여부
            apply_directly: True면 cmo_agent/에 직접 적용, False면 버전 디렉토리만 생성
        
        Returns:
            {
              "status": "success|failed",
              "version_name": "생성된 버전 이름",
              "applied_to_main": bool,
              "updated_layers": ["layer1", "layer2", ...],
              "changes_summary": "변경 사항 요약",
              "backup_path": "백업 경로 (if backup_current=True)"
            }
        """
        # 1. 버전 이름 생성
        if version_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_name = f"v_{timestamp}"
        
        print(f"\n🚀 새로운 CMO Agent 버전 생성: {version_name}")
        print("=" * 60)
        
        # 2. 현재 버전 백업 (완전한 cmo_agent_vX 디렉토리로)
        backup_path = None
        if backup_current:
            backup_path = self._backup_current_as_version(version_name)
            print(f"✅ 현재 버전 백업 완료: {backup_path}")
        
        # 3. sub_agents.py 수정
        updated_layers = []
        changes_summary = []
        
        try:
            # 원본 sub_agents.py 읽기
            original_sub_agents = self.cmo_agent_dir / "sub_agents.py"
            with open(original_sub_agents, 'r', encoding='utf-8') as f:
                sub_agents_content = f.read()
            
            # 각 레이어에 대한 프롬프트 업데이트 적용
            prompts = hr_output.get("prompts", [])
            
            for prompt_update in prompts:
                layer = prompt_update["layer"]
                new_prompt = prompt_update["new_prompt"]
                reason = prompt_update["reason"]
                expected_impact = prompt_update["expected_impact"]
                
                print(f"\n📝 {layer} 레이어 업데이트 중...")
                print(f"   이유: {reason}")
                print(f"   예상 효과: {expected_impact}")
                
                # sub_agents.py에서 해당 레이어의 프롬프트 교체
                sub_agents_content = self._update_layer_prompt(
                    sub_agents_content, 
                    layer, 
                    new_prompt
                )
                
                updated_layers.append(layer)
                changes_summary.append({
                    "layer": layer,
                    "reason": reason,
                    "expected_impact": expected_impact
                })
            
            # 4. 업데이트된 sub_agents.py를 cmo_agent/에 직접 적용
            if apply_directly:
                with open(original_sub_agents, 'w', encoding='utf-8') as f:
                    f.write(sub_agents_content)
                print(f"\n✅ cmo_agent/sub_agents.py 업데이트 완료")
            
            # 5. 메타데이터 저장 (백업 디렉토리에)
            if backup_path:
                metadata = {
                    "version_name": version_name,
                    "created_at": datetime.now().isoformat(),
                    "updated_layers": updated_layers,
                    "changes": changes_summary,
                    "thresholds": hr_output.get("thresholds", {}),
                    "global_adjustments": hr_output.get("global_adjustments", {}),
                    "is_backup": True
                }
                
                metadata_path = backup_path / "version_metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ 버전 {version_name} 적용 완료!")
            print(f"📂 백업: {backup_path}")
            print(f"📊 업데이트된 레이어: {', '.join(updated_layers)}")
            
            if apply_directly:
                print(f"\n🎯 cmo_agent/sub_agents.py가 직접 업데이트되었습니다!")
                print(f"   ADK가 새로운 프롬프트를 즉시 사용합니다.")
            
            return {
                "status": "success",
                "version_name": version_name,
                "applied_to_main": apply_directly,
                "updated_layers": updated_layers,
                "changes_summary": changes_summary,
                "backup_path": str(backup_path) if backup_path else None
            }
        
        except Exception as e:
            print(f"\n❌ 버전 적용 실패: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "failed",
                "error": str(e),
                "version_name": version_name
            }
    
    def _backup_current_as_version(self, next_version_name: str) -> Path:
        """
        현재 cmo_agent/를 완전한 cmo_agent_vX/ 디렉토리로 백업
        
        Args:
            next_version_name: 다음 버전 이름 (예: "v2")
        
        Returns:
            백업 디렉토리 경로 (예: cmo_agent_v1/)
        """
        # 현재 버전 번호 추출 또는 생성
        existing_versions = list(self.workspace_path.glob("cmo_agent_v*"))
        if existing_versions:
            # 가장 큰 버전 번호 찾기
            version_numbers = []
            for v in existing_versions:
                try:
                    num = int(v.name.replace("cmo_agent_v", ""))
                    version_numbers.append(num)
                except ValueError:
                    continue
            current_num = max(version_numbers) if version_numbers else 0
        else:
            current_num = 0
        
        # 백업 디렉토리 이름 (이전 버전)
        backup_dir = self.workspace_path / f"cmo_agent_v{current_num}"
        
        # 이미 존재하면 타임스탬프 추가
        if backup_dir.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.workspace_path / f"cmo_agent_v{current_num}_{timestamp}"
        
        # 전체 cmo_agent/ 디렉토리 복사
        shutil.copytree(
            self.cmo_agent_dir,
            backup_dir,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store')
        )
        
        return backup_dir
    
    def _update_layer_prompt(
        self, 
        content: str, 
        layer: str, 
        new_prompt: str
    ) -> str:
        """
        sub_agents.py에서 특정 레이어의 system_prompt 교체
        
        Args:
            content: sub_agents.py 전체 내용
            layer: 레이어 이름 (research, creative_writer, generator, etc.)
            new_prompt: 새로운 system prompt
        
        Returns:
            업데이트된 content
        """
        # 레이어 이름을 함수 이름으로 매핑
        layer_function_map = {
            "research": "create_research_agent",
            "creative_writer": "create_creative_writer_agent",
            "generator": "create_generator_agent",
            "critic": "create_critic_agent",
            "safety": "create_safety_agent",
            "selector": "create_selector_agent",
            "image_adapter": "create_image_adapter_agent"
        }
        
        function_name = layer_function_map.get(layer)
        if not function_name:
            print(f"⚠️ 알 수 없는 레이어: {layer}")
            return content
        
        # 함수 찾기
        function_start = content.find(f"def {function_name}()")
        if function_start == -1:
            print(f"⚠️ 함수를 찾을 수 없음: {function_name}")
            return content
        
        # system_prompt 시작 찾기
        prompt_start = content.find('system_prompt = """', function_start)
        if prompt_start == -1:
            prompt_start = content.find("system_prompt = '''", function_start)
            quote_type = "'''"
        else:
            quote_type = '"""'
        
        if prompt_start == -1:
            print(f"⚠️ system_prompt를 찾을 수 없음: {function_name}")
            return content
        
        # system_prompt 끝 찾기 (다음 함수 전까지)
        next_function = content.find("\ndef ", prompt_start + 20)
        search_end = next_function if next_function != -1 else len(content)
        
        prompt_end = content.find(f'{quote_type}', prompt_start + 20, search_end)
        
        if prompt_end == -1:
            print(f"⚠️ system_prompt 끝을 찾을 수 없음: {function_name}")
            return content
        
        # 프롬프트 교체
        before = content[:prompt_start + len(f'system_prompt = {quote_type}')]
        after = content[prompt_end:]
        
        # 새 프롬프트 포맷팅 (들여쓰기 유지)
        formatted_new_prompt = new_prompt.strip()
        
        updated_content = before + formatted_new_prompt + after
        
        return updated_content
    
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """생성된 모든 CMO Agent 버전 목록 조회 (cmo_agent_vX 형식)"""
        versions = []
        
        for version_dir in self.workspace_path.glob("cmo_agent_v*"):
            if version_dir.is_dir():
                metadata_path = version_dir / "version_metadata.json"
                
                version_info = {
                    "directory": version_dir.name,
                    "path": str(version_dir)
                }
                
                if metadata_path.exists():
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    version_info.update(metadata)
                else:
                    # 메타데이터 없으면 기본 정보만
                    version_info["created_at"] = datetime.fromtimestamp(
                        version_dir.stat().st_mtime
                    ).isoformat()
                
                versions.append(version_info)
        
        # 생성일 기준 정렬 (최신순)
        versions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return versions
    
    def restore_version(self, version_dir_name: str, backup_current: bool = True) -> Dict[str, Any]:
        """
        특정 버전으로 복원 (cmo_agent_vX → cmo_agent/)
        
        Args:
            version_dir_name: 복원할 버전 디렉토리 이름 (예: "cmo_agent_v1")
            backup_current: 복원 전 현재 버전 백업 여부
        """
        version_path = self.workspace_path / version_dir_name
        
        if not version_path.exists():
            return {
                "status": "failed",
                "error": f"버전을 찾을 수 없음: {version_dir_name}"
            }
        
        print(f"\n🔄 버전 복원: {version_dir_name}")
        
        # 현재 버전 백업
        if backup_current:
            backup_path = self._backup_current_as_version(f"before_restore")
            print(f"✅ 현재 버전 백업: {backup_path}")
        
        # 버전 파일들을 cmo_agent/에 복사
        files_to_restore = ["sub_agents.py", "agent.py", "tools.py", "__init__.py", "schemas.py"]
        
        for filename in files_to_restore:
            src = version_path / filename
            if src.exists():
                shutil.copy2(src, self.cmo_agent_dir / filename)
                print(f"✅ {filename} 복원")
        
        print(f"\n✅ 버전 {version_dir_name} 복원 완료!")
        
        return {
            "status": "success",
            "restored_from": version_dir_name,
            "restored_at": datetime.now().isoformat()
        }
    


def main():
    """CLI 사용 예제"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
CMO Agent Version Updater Tool

사용법:
  python version_updater.py create <hr_output.json> [version_name]
  python version_updater.py list
  python version_updater.py activate <version_name>
  python version_updater.py compare <version1> <version2>

예제:
  # HR Agent 출력으로부터 새 버전 생성
  python version_updater.py create hr_decisions_iteration_1.json v1.0
  
  # 모든 버전 목록 조회
  python version_updater.py list
  
  # 특정 버전 활성화
  python version_updater.py activate v1.0
  
  # 두 버전 비교
  python version_updater.py compare v1.0 v1.1
""")
        return
    
    command = sys.argv[1]
    updater = CMOVersionUpdater()
    
    if command == "create":
        if len(sys.argv) < 3:
            print("❌ HR output JSON 파일 경로가 필요합니다")
            return
        
        hr_output_path = sys.argv[2]
        version_name = sys.argv[3] if len(sys.argv) > 3 else None
        
        with open(hr_output_path, 'r', encoding='utf-8') as f:
            hr_output = json.load(f)
        
        result = updater.create_new_version(hr_output, version_name)
        print(f"\n결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    elif command == "list":
        versions = updater.list_versions()
        print(f"\n📋 총 {len(versions)}개 버전:")
        for v in versions:
            print(f"\n- {v['version_name']}")
            print(f"  생성일: {v['created_at']}")
            print(f"  레이어: {', '.join(v['updated_layers'])}")
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("❌ 버전 이름이 필요합니다")
            return
        
        version_name = sys.argv[2]
        result = updater.activate_version(version_name)
        print(f"\n결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    elif command == "compare":
        if len(sys.argv) < 4:
            print("❌ 두 개의 버전 이름이 필요합니다")
            return
        
        v1 = sys.argv[2]
        v2 = sys.argv[3]
        result = updater.compare_versions(v1, v2)
        print(f"\n비교 결과:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
    
    else:
        print(f"❌ 알 수 없는 명령: {command}")


if __name__ == "__main__":
    main()

