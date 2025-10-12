# CMO Agent 자동 버전 관리 가이드

HR Validation Agent가 ADK tool을 사용하여 자동으로 CMO Agent의 새 버전을 생성하는 통합 워크플로우입니다.

## 🎯 개요

이 시스템은 HR Agent와 CMO Agent 버전 관리를 완전히 통합했습니다:

1. **HR Agent 실행** → 프롬프트 개선 결정
2. **Tool 자동 호출** → 새 CMO 버전 자동 생성
3. **선택적 활성화** → 즉시 또는 수동으로 활성화

더 이상 별도 스크립트 실행이 필요 없습니다!

## 🚀 빠른 시작

### 방법 1: 자동화된 워크플로우 (추천)

```bash
python run_hr_with_auto_versioning.py --quick
```

이 명령어는:
- ✅ HR Agent 실행
- ✅ 성능 분석 및 개선 결정
- ✅ 자동으로 새 CMO 버전 생성
- ✅ 백업 자동 생성
- ℹ️ 활성화는 수동 (안전)

### 방법 2: 대화형 모드

```bash
python run_hr_with_auto_versioning.py
```

대화형으로:
- 입력 파일 선택
- 버전 이름 지정
- 즉시 활성화 여부 선택

## 📖 상세 사용법

### Python 코드로 사용

```python
import asyncio
from run_hr_with_auto_versioning import run_hr_with_auto_versioning

# 실행
result = asyncio.run(run_hr_with_auto_versioning(
    input_json_path="hr_input_with_actual_performance.json",
    version_name="v1.1_engagement_boost",
    auto_activate=False
))

if result and result.get("status") == "success":
    print(f"새 버전 생성: {result['version_name']}")
    print(f"경로: {result['version_path']}")
```

### HR Agent에서 직접 Tool 사용

HR Agent 실행 중에 자동으로 tool이 호출되거나, 수동으로 호출할 수 있습니다:

```python
# HR Agent 내부에서
# 1. 결정 생성
hr_decisions = {
    "prompts": [...],
    "thresholds": {...}
}

# 2. Tool 호출 (HR Agent가 자동으로 할 수 있음)
result = create_cmo_version_from_hr_output(
    hr_decisions_json=json.dumps(hr_decisions),
    version_name="v1.0",
    backup_current=True,
    auto_activate=False
)
```

## 🔧 사용 가능한 Tools

HR Agent에 통합된 CMO 버전 관리 tools:

### 1. `create_cmo_version_from_hr_output`

HR 결정으로부터 새 CMO 버전 생성

**Parameters:**
- `hr_decisions_json` (str): HR 결정 JSON 문자열
- `version_name` (str, optional): 버전 이름
- `backup_current` (bool): 백업 여부 (기본: True)
- `auto_activate` (bool): 즉시 활성화 (기본: False)

**Returns:** JSON 문자열
```json
{
  "status": "success",
  "version_name": "v_20251012_153000",
  "version_path": "/path/to/version",
  "updated_layers": ["research", "creative_writer"],
  "backup_path": "/path/to/backup",
  "activated": false
}
```

### 2. `activate_cmo_version`

특정 버전을 활성화

**Parameters:**
- `version_name` (str): 활성화할 버전 이름
- `backup_current` (bool): 백업 여부 (기본: True)

### 3. `list_cmo_versions`

모든 버전 목록 조회

**Returns:** 버전 목록 JSON

### 4. `compare_cmo_versions`

두 버전 비교

**Parameters:**
- `version1` (str): 첫 번째 버전
- `version2` (str): 두 번째 버전

### 5. `get_version_metadata`

버전 메타데이터 조회

**Parameters:**
- `version_name` (str): 버전 이름

## 🔄 완전 자동화 워크플로우

### 시나리오 1: 성능 모니터링 → 자동 개선

```bash
# 1. 현재 성능 데이터 수집 (실제 engagement 포함)
# hr_input_with_actual_performance.json 업데이트

# 2. 자동 분석 및 버전 생성
python run_hr_with_auto_versioning.py --quick

# 3. 새 버전 확인
ls -la cmo_agent_versions/

# 4. 만족하면 활성화
python -c "from cmo_agent.tools_version import activate_cmo_version; print(activate_cmo_version('v_20251012_153000'))"

# 5. 테스트
python test_cmo_agent.py
```

### 시나리오 2: 수동 제어 + 즉시 활성화

```python
import asyncio
from run_hr_with_auto_versioning import run_hr_with_auto_versioning

async def deploy_new_version():
    result = await run_hr_with_auto_versioning(
        input_json_path="hr_input_with_actual_performance.json",
        version_name="v1.2_production",
        auto_activate=True  # 즉시 활성화!
    )
    
    if result and result.get("activated"):
        print("✅ 새 버전이 프로덕션에 배포되었습니다!")
        # 알림, 로깅 등...
    
    return result

asyncio.run(deploy_new_version())
```

## 📊 HR Agent Instruction 업데이트

HR Agent에 다음이 추가되었습니다:

```
## CMO VERSION MANAGEMENT (OPTIONAL)

After making your decisions, you can OPTIONALLY use these tools to automatically 
create a new CMO Agent version:

**Tool: create_cmo_version_from_hr_output**
- Creates a new CMO Agent version from your decision JSON
- Args:
  * hr_decisions_json: Your complete output JSON (as string)
  * version_name: Optional version name
  * backup_current: Whether to backup current version (default: true)
  * auto_activate: Whether to immediately activate new version (default: false)
```

HR Agent는 이제:
1. 성능 분석
2. 개선 결정
3. **자동으로 새 버전 생성** (선택적)
4. 결과 반환

모든 과정을 한 번의 실행으로 완료합니다!

## 🎨 고급 활용

### A/B 테스팅 자동화

```python
import asyncio

# 두 가지 다른 접근 방식으로 버전 생성
async def ab_test():
    # A: 공격적인 viral 최적화
    result_a = await run_hr_with_auto_versioning(
        input_json_path="hr_input_aggressive.json",
        version_name="v_test_aggressive"
    )
    
    # B: 균형잡힌 접근
    result_b = await run_hr_with_auto_versioning(
        input_json_path="hr_input_balanced.json",
        version_name="v_test_balanced"
    )
    
    # 각각 테스트하고 비교
    # ...

asyncio.run(ab_test())
```

### 스케줄된 최적화

```python
import asyncio
import schedule
import time

def scheduled_optimization():
    """매일 자동으로 성능 분석 및 최적화"""
    asyncio.run(run_hr_with_auto_versioning(
        input_json_path="hr_input_daily.json",
        version_name=f"v_daily_{time.strftime('%Y%m%d')}",
        auto_activate=False  # 수동 검토 후 활성화
    ))

# 매일 오전 9시에 실행
schedule.every().day.at("09:00").do(scheduled_optimization)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📁 파일 구조

```
agents_of_agents/
├── hr_validation_agent/
│   └── agent.py                        # HR Agent (tools 통합됨)
│
├── cmo_agent/
│   ├── agent.py                        # 현재 활성 CMO Agent
│   ├── sub_agents.py                   # 레이어 정의
│   ├── tools_version.py                # ⭐ 버전 관리 tools
│   └── version_updater.py              # 핵심 버전 관리 로직
│
├── cmo_agent_versions/                 # 모든 버전 저장소
│   ├── v_20251012_150000/
│   │   ├── sub_agents.py
│   │   ├── version_metadata.json
│   │   └── README.md
│   └── v_20251012_160000/
│       └── ...
│
├── run_hr_with_auto_versioning.py      # ⭐ 통합 실행 스크립트
├── hr_input_with_actual_performance.json
└── hr_decisions_iteration_N.json       # HR 결정 저장
```

## 🔒 안전 기능

1. **자동 백업**: 모든 버전 생성 시 현재 버전 자동 백업
2. **수동 활성화**: 기본적으로 자동 활성화 비활성화 (안전)
3. **메타데이터 추적**: 모든 변경사항 기록
4. **롤백 가능**: 이전 버전으로 쉽게 복원

## ⚠️ 주의사항

1. **테스트 필수**: 새 버전을 프로덕션에 활성화하기 전 충분히 테스트
2. **백업 확인**: 백업이 제대로 생성되었는지 확인
3. **Git 커밋**: 중요한 버전은 Git에도 커밋
4. **성능 모니터링**: 새 버전 활성화 후 성능 추적

## 🆚 이전 방식과 비교

### 이전 (별도 스크립트)

```bash
# 1. HR Agent 실행
python test_hr_agent.py

# 2. 결과 확인
cat hr_decisions_iteration_1.json

# 3. 수동으로 버전 생성
python apply_hr_improvements.py

# 4. 수동으로 활성화
python cmo_agent/version_updater.py activate v1.0

# 총 4단계
```

### 현재 (ADK Tools 통합)

```bash
# 1. 자동화된 워크플로우
python run_hr_with_auto_versioning.py --quick

# 완료! (필요시 수동 활성화만 추가)
```

**장점:**
- ✅ 한 번의 명령으로 완료
- ✅ HR Agent가 직접 tool 호출
- ✅ 에러 처리 자동화
- ✅ 더 나은 추적 및 로깅

## 📚 관련 문서

- **버전 관리 기본**: `CMO_VERSION_UPDATER_GUIDE.md`
- **HR Agent 사용법**: `HR_VALIDATION_USAGE.md`
- **CMO 아키텍처**: `A2A_ARCHITECTURE.md`

## 💡 팁

1. **버전 네이밍**: 의미있는 이름 사용 (e.g., `v1.0_viral_boost`)
2. **정기 최적화**: 일주일에 한 번 성능 분석 및 최적화
3. **실험적 버전**: 실험용 버전은 `v_test_*` 형식으로 네이밍
4. **프로덕션 버전**: 안정화된 버전은 `v1.0`, `v1.1` 등 시맨틱 버전

---

**만든 이**: CMO Agent Development Team  
**버전**: 2.0 (ADK Tools 통합)  
**마지막 업데이트**: 2025-10-12

