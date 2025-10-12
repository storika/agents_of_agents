# CMO Agent Version Updater 가이드

HR Validation Agent의 프롬프트 개선 결과를 CMO Agent에 적용하여 새로운 버전을 생성하는 도구입니다.

## 🎯 주요 기능

1. **자동 버전 생성**: HR Agent의 출력을 기반으로 새로운 CMO Agent 버전 자동 생성
2. **백업 관리**: 기존 버전 자동 백업
3. **버전 관리**: 여러 버전 생성 및 관리
4. **버전 활성화**: 원하는 버전으로 쉽게 전환
5. **버전 비교**: 서로 다른 버전 간 차이점 비교

## 🚀 빠른 시작

### 방법 1: 간편 스크립트 사용 (추천)

제공된 HR validation 결과를 바로 적용:

```bash
python apply_hr_improvements.py
```

이 스크립트는:
- HR validation 결과가 이미 포함되어 있음
- 대화형으로 버전 이름 입력
- 자동으로 백업 생성
- 선택적으로 즉시 활성화 가능

### 방법 2: 커스텀 HR 출력 사용

자체 HR validation 결과 파일이 있는 경우:

```bash
python cmo_agent/version_updater.py create your_hr_output.json v1.1
```

## 📖 상세 사용법

### 1. 새 버전 생성

#### Python 코드로 생성

```python
from cmo_agent.version_updater import CMOVersionUpdater

# HR validation 결과
hr_output = {
    "prompts": [
        {
            "layer": "research",
            "new_prompt": "새로운 research layer 프롬프트...",
            "reason": "변경 이유",
            "expected_impact": "예상 효과"
        },
        # ... 더 많은 레이어
    ],
    "thresholds": {
        "clarity": 0.55,
        "novelty": 0.55,
        "shareability": 0.55
    }
}

# 버전 생성
updater = CMOVersionUpdater()
result = updater.create_new_version(
    hr_output=hr_output,
    version_name="v1.0",  # 선택사항, None이면 타임스탬프 사용
    backup_current=True   # 현재 버전 백업 여부
)

print(result)
# {
#   "status": "success",
#   "version_name": "v1.0",
#   "version_path": "/path/to/cmo_agent_versions/v1.0",
#   "updated_layers": ["research", "creative_writer", "generator"],
#   "backup_path": "/path/to/backup"
# }
```

#### CLI로 생성

```bash
# JSON 파일로부터 생성
python cmo_agent/version_updater.py create hr_decisions_iteration_1.json

# 버전 이름 지정
python cmo_agent/version_updater.py create hr_decisions_iteration_1.json v1.0
```

### 2. 버전 목록 조회

```bash
python cmo_agent/version_updater.py list
```

출력 예시:
```
📋 총 3개 버전:

- v1.0
  생성일: 2025-10-12T15:30:00
  레이어: research, creative_writer, generator

- v_20251012_143000
  생성일: 2025-10-12T14:30:00
  레이어: research, generator

- v0.9
  생성일: 2025-10-11T10:00:00
  레이어: creative_writer, safety
```

Python 코드:
```python
updater = CMOVersionUpdater()
versions = updater.list_versions()

for v in versions:
    print(f"{v['version_name']}: {v['updated_layers']}")
```

### 3. 버전 활성화

특정 버전을 현재 CMO Agent에 적용:

```bash
python cmo_agent/version_updater.py activate v1.0
```

Python 코드:
```python
updater = CMOVersionUpdater()
result = updater.activate_version("v1.0", backup_current=True)

# {
#   "status": "success",
#   "version_name": "v1.0",
#   "activated_at": "2025-10-12T15:35:00"
# }
```

⚠️ **주의**: 활성화하면 현재 `cmo_agent/` 디렉토리의 파일들이 교체됩니다. `backup_current=True`로 백업을 먼저 생성하세요.

### 4. 버전 비교

두 버전의 차이점 비교:

```bash
python cmo_agent/version_updater.py compare v1.0 v1.1
```

Python 코드:
```python
updater = CMOVersionUpdater()
comparison = updater.compare_versions("v1.0", "v1.1")

print(f"공통 레이어: {comparison['common_layers']}")
print(f"v1.0에만 있음: {comparison['only_in_v1']}")
print(f"v1.1에만 있음: {comparison['only_in_v2']}")
```

## 📁 디렉토리 구조

버전이 생성되면 다음과 같은 구조가 만들어집니다:

```
agents_of_agents/
├── cmo_agent/                    # 현재 활성 버전
│   ├── agent.py
│   ├── sub_agents.py            # 레이어 정의
│   ├── tools.py
│   └── version_updater.py       # 이 도구
│
├── cmo_agent_versions/          # 모든 버전 저장소
│   ├── v1.0/
│   │   ├── sub_agents.py        # 업데이트된 레이어 프롬프트
│   │   ├── agent.py
│   │   ├── tools.py
│   │   ├── version_metadata.json  # 버전 메타데이터
│   │   └── README.md            # 버전 설명
│   │
│   ├── v1.0_backup/             # v1.0 생성 전 백업
│   │   ├── sub_agents.py
│   │   └── agent.py
│   │
│   └── v1.1/
│       └── ...
│
└── apply_hr_improvements.py     # 간편 적용 스크립트
```

## 🔧 HR Validation 결과 형식

`version_updater`가 기대하는 HR output 형식:

```json
{
  "prompts": [
    {
      "layer": "research|creative_writer|generator|critic|safety|selector|image_adapter",
      "new_prompt": "완전한 새 system prompt 텍스트...",
      "reason": "왜 이 프롬프트를 변경하는가",
      "expected_impact": "예상되는 성능 향상"
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
```

### 지원되는 레이어

1. **research** - `create_research_agent()`
2. **creative_writer** - `create_creative_writer_agent()`
3. **generator** - `create_generator_agent()`
4. **critic** - `create_critic_agent()`
5. **safety** - `create_safety_agent()`
6. **selector** - `create_selector_agent()`
7. **image_adapter** - `create_image_adapter_agent()`

## 📊 워크플로우 예제

### 전형적인 개선 사이클

```bash
# 1. HR Agent 실행하여 개선 사항 파악
python test_hr_agent.py

# 2. HR 출력이 hr_decisions_iteration_1.json으로 저장됨

# 3. 새 버전 생성
python cmo_agent/version_updater.py create hr_decisions_iteration_1.json v1.1

# 4. 버전 확인
cd cmo_agent_versions/v1.1
cat README.md

# 5. 테스트 (아직 활성화하지 않고)
# (테스트 코드에서 version_path를 지정하여 새 버전 테스트)

# 6. 만족하면 활성화
python cmo_agent/version_updater.py activate v1.1

# 7. 실제 CMO Agent 실행
python test_cmo_agent.py

# 8. 문제가 있으면 이전 버전으로 롤백
python cmo_agent/version_updater.py activate v1.0
```

## 🎨 고급 사용법

### 버전별로 다른 프롬프트 실험

```python
from cmo_agent.version_updater import CMOVersionUpdater

updater = CMOVersionUpdater()

# A/B 테스트를 위한 두 버전 생성
hr_output_aggressive = {...}  # 공격적인 viral 프롬프트
hr_output_balanced = {...}    # 균형잡힌 프롬프트

updater.create_new_version(hr_output_aggressive, "v_aggressive")
updater.create_new_version(hr_output_balanced, "v_balanced")

# 각각 테스트하고 성능 비교
# ...

# 더 나은 버전 활성화
updater.activate_version("v_balanced")
```

### 수동으로 버전 수정

```bash
# 1. 버전 생성
python cmo_agent/version_updater.py create hr_output.json v1.2

# 2. 수동으로 추가 수정
vim cmo_agent_versions/v1.2/sub_agents.py

# 3. 메타데이터 업데이트 (선택사항)
# version_metadata.json에 변경 사항 기록

# 4. 활성화
python cmo_agent/version_updater.py activate v1.2
```

## ⚠️ 주의사항

1. **백업 필수**: 활성화 전 항상 현재 버전을 백업하세요 (`backup_current=True`)
2. **테스트**: 새 버전을 활성화하기 전에 충분히 테스트하세요
3. **Git 커밋**: 중요한 버전은 Git에도 커밋하세요
4. **메타데이터 보존**: `version_metadata.json`을 삭제하지 마세요

## 🐛 트러블슈팅

### 문제: 버전 생성 실패

```
❌ 함수를 찾을 수 없음: create_xxx_agent
```

**해결**: `layer` 이름이 정확한지 확인하세요. 지원되는 레이어: research, creative_writer, generator, critic, safety, selector, image_adapter

### 문제: 활성화 후 import 오류

```python
ImportError: cannot import name 'create_research_agent'
```

**해결**: 
1. Python 캐시 삭제: `rm -rf cmo_agent/__pycache__`
2. Python 재시작
3. 파일 권한 확인

### 문제: 프롬프트가 제대로 교체되지 않음

**해결**:
1. `sub_agents.py`에서 `system_prompt = """` 형식이 일치하는지 확인
2. 수동으로 버전 파일을 열어서 프롬프트가 올바른지 확인
3. 필요시 수동 수정 후 재활성화

## 📚 추가 리소스

- **HR Validation Agent**: `HR_VALIDATION_USAGE.md`
- **CMO Agent 아키텍처**: `A2A_ARCHITECTURE.md`
- **Sequential Layers**: `SEQUENTIAL_LAYERS_README.md`

## 💡 팁

1. **버전 네이밍**: 의미있는 이름 사용 (e.g., `v_viral_optimized`, `v_safety_enhanced`)
2. **점진적 개선**: 한 번에 너무 많은 레이어를 변경하지 말고, 점진적으로 개선
3. **성능 추적**: 각 버전의 실제 engagement 지표를 기록하여 비교
4. **문서화**: `version_metadata.json`에 추가 노트 작성

---

**만든 이**: CMO Agent Development Team  
**버전**: 1.0  
**마지막 업데이트**: 2025-10-12

