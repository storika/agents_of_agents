# CMO Agent - X 포스팅 기능 가이드

CMO Agent에 실제 X(Twitter) 포스팅 기능이 추가되었습니다.

## 🎯 주요 기능

- ✅ **OAuth 2.0 인증**: test.py를 참고한 안전한 OAuth 2.0 방식
- ✅ **사용자 승인 필수**: 자동 포스팅 없음, 항상 사용자 동의 후 포스팅
- ✅ **완전한 워크플로우**: 콘텐츠 생성 → 미리보기 → 승인 → 포스팅
- ✅ **Weave 통합**: 모든 과정이 Weave로 트래킹됨

## 📋 사전 준비

### 1. Twitter API 설정

Twitter Developer Portal에서 OAuth 2.0 설정:

1. https://developer.twitter.com/en/portal/dashboard 접속
2. 앱 생성 또는 선택
3. **Settings** → **User authentication settings**
4. 다음 설정 확인:
   - **App permissions**: `Read and Write`
   - **Type of App**: `Web App`
   - **Callback URI / Redirect URL**: `http://localhost:8080/callback`
5. **Keys and tokens** → **OAuth 2.0 Client ID and Client Secret** 확인

### 2. 환경 변수 설정

`.env` 파일에 추가:

```bash
# Twitter OAuth 2.0
TW_CLIENT_ID=your_client_id_here
TW_CLIENT_SECRET=your_client_secret_here
```

### 3. OAuth 2.0 토큰 발급

```bash
python oauth2_setup.py
```

이 스크립트가:
1. 로컬 서버를 `localhost:8080`에서 시작
2. 브라우저를 열어 Twitter 인증 페이지로 이동
3. 앱 승인 후 자동으로 Access Token과 Refresh Token을 `.env`에 저장

성공하면 `.env`에 자동으로 추가됨:
```bash
TW_OAUTH2_ACCESS_TOKEN=your_access_token
TW_OAUTH2_REFRESH_TOKEN=your_refresh_token
```

## 🚀 사용 방법

### 방법 1: 예제 스크립트 실행

```bash
# 단일 실행 모드
python examples/cmo_with_x_posting.py

# 대화형 모드
python examples/cmo_with_x_posting.py --interactive
```

### 방법 2: Python 코드에서 직접 사용

```python
from cmo_agent.agent import root_agent

# 1단계: 콘텐츠 생성 요청
result = root_agent.run("Give me next content for X/Twitter")
print(result)

# Agent가 콘텐츠를 생성하고 승인을 요청합니다.
# 출력 예시:
# """
# [생성된 콘텐츠 미리보기]
# 트윗 텍스트: "Behind the scenes: Our LoopAgent tried 3 times..."
# 이미지: artifacts/generated_image.png
# 예상 성과: 8.5-9% engagement
# 
# 이 콘텐츠를 X에 포스팅할까요? (승인하려면 'yes' 또는 '포스팅'이라고 답해주세요)
# """

# 2단계: 승인 (새로운 대화로)
result = root_agent.run("yes")  # 또는 "포스팅"

# 포스팅 완료!
# 출력 예시:
# """
# ✅ 포스팅 완료! https://twitter.com/i/web/status/1234567890
# """
```

### 방법 3: 명령줄에서 직접 테스트

```bash
# 간단한 트윗 테스트 (test.py 사용)
uv run test.py --text "Hello from CMO Agent! 🤖"
```

## 📊 워크플로우

```
1. 콘텐츠 생성 요청
   ↓
2. Research Agent → 트렌드 분석
   ↓
3. ContentGenerationLoop (3회 반복)
   → Writer → Generator → Critic
   ↓
4. Safety Agent → 안전성 검증
   ↓
5. Selector Agent → 최적 콘텐츠 선택
   ↓
6. Image Generator → 이미지 생성
   ↓
7. 사용자에게 미리보기 제공
   → 트윗 텍스트
   → 생성된 이미지
   → 성과 예측
   ↓
8. 사용자 승인 대기 ⏸️
   ↓
9. 승인 시 → X에 실제 포스팅 🚀
   ↓
10. 트윗 URL 반환 및 메트릭 저장
```

## 🔒 안전 기능

### 1. 필수 사용자 승인
- Agent는 **절대로** 자동으로 포스팅하지 않습니다
- 항상 사용자에게 미리보기를 보여주고 승인을 요청합니다

### 2. 시뮬레이션 모드
토큰이 설정되지 않았거나 API 호출이 실패하면:
- 자동으로 시뮬레이션 모드로 전환
- 실제 포스팅 없이 워크플로우만 테스트

### 3. 에러 처리
- 403 Forbidden: 권한 문제 감지 및 해결 방법 안내
- 429 Rate Limit: 자동 재시도 (최대 3회)
- 네트워크 오류: 자동 재시도 및 폴백

## 🛠️ 고급 사용법

### x_publish 함수 직접 사용

```python
from cmo_agent.tools import x_publish

# 실제 포스팅
result = x_publish(
    text="Your tweet text here",
    media_prompt="Image generation prompt",
    mode="image",
    require_approval=False,  # True면 큐에만 추가
    actually_post=True       # False면 시뮬레이션
)

print(result)
```

### 파라미터 설명

- `text`: 트윗 텍스트 (필수)
- `media_prompt`: 이미지 생성 프롬프트 (향후 이미지 업로드 기능용)
- `mode`: 미디어 타입 ("image", "video", "gif")
- `require_approval`: True면 큐에만 추가, False면 즉시 처리
- `actually_post`: True면 실제 API 호출, False면 시뮬레이션

## 📈 메트릭 및 학습

포스팅 후 자동으로 메트릭이 저장됩니다:

```json
{
  "iteration": 1,
  "timestamp": "2025-10-12T...",
  "selected_candidate": {
    "text": "...",
    "media_prompt": "...",
    "scores": {...}
  },
  "tweet_id": "1234567890",
  "tweet_url": "https://twitter.com/...",
  "predicted_score": 0.87
}
```

이 데이터는 다음 콘텐츠 생성 시 학습에 활용됩니다.

## ❓ FAQ

### Q: 토큰이 만료되면?

A: `oauth2_setup.py`를 다시 실행하여 새 토큰을 발급받으세요.

### Q: 테스트 환경에서 실제 포스팅하고 싶지 않은데?

A: `actually_post=False`로 설정하면 시뮬레이션 모드로 동작합니다.

### Q: 이미지도 함께 업로드할 수 있나요?

A: 현재는 텍스트만 포스팅됩니다. 이미지 업로드 기능은 추후 추가 예정입니다.

### Q: 여러 트윗을 연속으로 포스팅하려면?

A: `test.py`의 `--messages` 옵션을 사용하세요:

```bash
# messages.txt 파일에 트윗 목록 작성 (한 줄에 하나씩)
uv run test.py --messages messages.txt --wrap
```

## 🐛 트러블슈팅

### 403 Forbidden 에러

**원인**: App permissions가 Read-only로 설정됨

**해결**:
1. Developer Portal → Settings → User authentication settings
2. App permissions를 `Read and Write`로 변경
3. `python oauth2_setup.py` 재실행하여 새 토큰 발급

### 로컬 서버 포트 충돌

**원인**: 8080 포트가 이미 사용 중

**해결**:
```bash
# 기존 프로세스 종료
lsof -ti:8080 | xargs kill -9

# 또는 oauth2_setup.py의 REDIRECT_URI 포트 변경
```

### Redirect URI 불일치

**원인**: Developer Portal의 설정과 코드의 설정이 다름

**해결**:
Developer Portal에 정확히 `http://localhost:8080/callback` 추가

## 📚 참고 자료

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [OAuth 2.0 Authorization Code Flow](https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code)
- [test.py](../test.py) - OAuth 2.0 구현 참고
- [oauth2_setup.py](../oauth2_setup.py) - 토큰 발급 스크립트

