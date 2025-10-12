"""
CMO Version Updater 테스트 스크립트
"""

from cmo_agent.version_updater import CMOVersionUpdater
import json


def test_create_version():
    """버전 생성 테스트"""
    print("\n" + "=" * 70)
    print("테스트 1: 새 버전 생성")
    print("=" * 70)
    
    # 테스트용 HR output
    test_hr_output = {
        "prompts": [
            {
                "layer": "research",
                "new_prompt": """You are the Research layer TEST VERSION. This is a test prompt to verify version updater functionality.

Input: A broad topic or industry to investigate.

Instructions:
1. Identify trending topics
2. Analyze audience interests
3. Propose viral angles

Output MUST be a JSON object with:
- trending_topics: array
- audience_insights: string
- viral_potential_angles: array

TEST VERSION - DO NOT USE IN PRODUCTION
""",
                "reason": "Test version creation functionality",
                "expected_impact": "Verify that version updater can correctly update layer prompts"
            }
        ],
        "thresholds": {
            "clarity": 0.60,
            "novelty": 0.60,
            "shareability": 0.60
        }
    }
    
    updater = CMOVersionUpdater()
    
    result = updater.create_new_version(
        hr_output=test_hr_output,
        version_name="test_version",
        backup_current=True
    )
    
    if result["status"] == "success":
        print("✅ 버전 생성 성공!")
        print(f"   버전: {result['version_name']}")
        print(f"   경로: {result['version_path']}")
        print(f"   레이어: {', '.join(result['updated_layers'])}")
        return True
    else:
        print(f"❌ 버전 생성 실패: {result.get('error')}")
        return False


def test_list_versions():
    """버전 목록 조회 테스트"""
    print("\n" + "=" * 70)
    print("테스트 2: 버전 목록 조회")
    print("=" * 70)
    
    updater = CMOVersionUpdater()
    versions = updater.list_versions()
    
    print(f"✅ 총 {len(versions)}개 버전 발견:")
    for v in versions:
        print(f"\n   - {v['version_name']}")
        print(f"     생성일: {v.get('created_at', 'N/A')}")
        print(f"     레이어: {', '.join(v.get('updated_layers', []))}")
    
    return len(versions) > 0


def test_compare_versions():
    """버전 비교 테스트"""
    print("\n" + "=" * 70)
    print("테스트 3: 버전 비교")
    print("=" * 70)
    
    updater = CMOVersionUpdater()
    versions = updater.list_versions()
    
    if len(versions) < 2:
        print("⚠️ 비교할 버전이 2개 미만입니다. 테스트 스킵.")
        return True
    
    v1_name = versions[0]['version_name']
    v2_name = versions[1]['version_name']
    
    print(f"비교: {v1_name} vs {v2_name}")
    
    result = updater.compare_versions(v1_name, v2_name)
    
    if result["status"] == "success":
        print(f"✅ 비교 성공!")
        print(f"   공통 레이어: {result['common_layers']}")
        print(f"   {v1_name}에만: {result['only_in_v1']}")
        print(f"   {v2_name}에만: {result['only_in_v2']}")
        return True
    else:
        print(f"❌ 비교 실패: {result.get('error')}")
        return False


def test_version_metadata():
    """버전 메타데이터 확인 테스트"""
    print("\n" + "=" * 70)
    print("테스트 4: 버전 메타데이터 확인")
    print("=" * 70)
    
    updater = CMOVersionUpdater()
    versions = updater.list_versions()
    
    if not versions:
        print("⚠️ 버전이 없습니다. 테스트 스킵.")
        return True
    
    # 가장 최신 버전 확인
    latest = versions[0]
    version_path = updater.versions_dir / latest['version_name']
    metadata_path = version_path / "version_metadata.json"
    
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"✅ 메타데이터 발견: {latest['version_name']}")
        print(f"\n메타데이터 내용:")
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
        return True
    else:
        print(f"❌ 메타데이터 파일 없음: {metadata_path}")
        return False


def test_readme_exists():
    """README 파일 존재 확인"""
    print("\n" + "=" * 70)
    print("테스트 5: README 파일 확인")
    print("=" * 70)
    
    updater = CMOVersionUpdater()
    versions = updater.list_versions()
    
    if not versions:
        print("⚠️ 버전이 없습니다. 테스트 스킵.")
        return True
    
    latest = versions[0]
    version_path = updater.versions_dir / latest['version_name']
    readme_path = version_path / "README.md"
    
    if readme_path.exists():
        print(f"✅ README 발견: {latest['version_name']}")
        print(f"\nREADME 미리보기 (처음 20줄):")
        print("-" * 70)
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[:20]:
                print(line.rstrip())
        if len(lines) > 20:
            print(f"... ({len(lines) - 20}줄 더 있음)")
        return True
    else:
        print(f"❌ README 파일 없음: {readme_path}")
        return False


def main():
    """전체 테스트 실행"""
    print("\n" + "=" * 70)
    print("CMO Version Updater 테스트 시작")
    print("=" * 70)
    
    tests = [
        ("버전 생성", test_create_version),
        ("버전 목록 조회", test_list_versions),
        ("버전 비교", test_compare_versions),
        ("메타데이터 확인", test_version_metadata),
        ("README 확인", test_readme_exists)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 테스트 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("테스트 결과 요약")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 70)
    print(f"총 {passed}/{total}개 테스트 통과")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 모든 테스트가 통과했습니다!")
        print("\n다음 단계:")
        print("1. python apply_hr_improvements.py - HR 개선사항 적용")
        print("2. python test_cmo_agent.py - CMO Agent 테스트")
    else:
        print(f"\n⚠️ {total - passed}개의 테스트가 실패했습니다.")
        print("위의 오류 메시지를 확인하세요.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

