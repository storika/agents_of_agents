#!/usr/bin/env python3
"""
Twitter OAuth 2.0 User Context 인증 헬퍼

Client ID와 Client Secret을 사용하여 Access Token과 Refresh Token을 발급받습니다.
"""

import os
import sys
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse
import threading

# OAuth 2.0 개발 환경에서 localhost HTTP 허용
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import tweepy
from dotenv import load_dotenv, set_key

# PKCE Flow를 위한 설정
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]

# Callback에서 받은 코드를 저장할 전역 변수
auth_code = None
auth_error = None

class CallbackHandler(BaseHTTPRequestHandler):
    """OAuth callback을 받기 위한 HTTP 핸들러"""
    
    def do_GET(self):
        global auth_code, auth_error
        
        # 전체 callback URL 저장 (state 포함)
        full_url = f"http://localhost:8080{self.path}"
        
        # URL 파싱
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        if 'code' in params:
            auth_code = full_url  # 전체 URL 저장
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>✅ 인증 성공!</h1>
                    <p>이 창을 닫고 터미널로 돌아가세요.</p>
                </body>
                </html>
            """.encode('utf-8'))
        elif 'error' in params:
            auth_error = params['error'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1>❌ 인증 실패</h1>
                    <p>에러: {auth_error}</p>
                    <p>이 창을 닫고 터미널로 돌아가세요.</p>
                </body>
                </html>
            """.encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
    
    def log_message(self, format, *args):
        # 로그 출력 억제
        pass

def load_credentials():
    """Client ID와 Secret 로드"""
    load_dotenv()
    client_id = os.getenv("TW_CLIENT_ID")
    client_secret = os.getenv("TW_CLIENT_SECRET")
    
    if not client_id:
        print("[ERROR] TW_CLIENT_ID가 .env 파일에 없습니다.", file=sys.stderr)
        print("Twitter Developer Portal에서 Client ID를 받아 .env에 추가하세요.\n", file=sys.stderr)
        sys.exit(1)
    
    # Client Secret은 Public Client의 경우 필요없을 수 있음
    return client_id, client_secret


def refresh_access_token():
    """Refresh Token을 사용해서 새로운 Access Token 발급"""
    load_dotenv()
    
    client_id = os.getenv("TW_CLIENT_ID")
    client_secret = os.getenv("TW_CLIENT_SECRET")
    refresh_token = os.getenv("TW_OAUTH2_REFRESH_TOKEN")
    
    if not client_id:
        print("[ERROR] TW_CLIENT_ID가 .env 파일에 없습니다.", file=sys.stderr)
        sys.exit(1)
    
    if not refresh_token:
        print("[ERROR] TW_OAUTH2_REFRESH_TOKEN이 .env 파일에 없습니다.", file=sys.stderr)
        print("oauth2_setup.py를 먼저 실행하여 Refresh Token을 발급받으세요.\n", file=sys.stderr)
        sys.exit(1)
    
    print("Refresh Token으로 Access Token을 갱신합니다...\n")
    
    try:
        # OAuth2UserHandler 생성
        oauth2_user_handler = tweepy.OAuth2UserHandler(
            client_id=client_id,
            redirect_uri=REDIRECT_URI,
            scope=SCOPES,
            client_secret=client_secret
        )
        
        # Refresh token으로 새 access token 발급
        new_token = oauth2_user_handler.refresh_token(
            f"https://api.twitter.com/2/oauth2/token",
            refresh_token=refresh_token,
            body=f"grant_type=refresh_token&client_id={client_id}"
        )
        
        print("✅ Access Token 갱신 성공!")
        print(f"New Access Token: {new_token['access_token'][:20]}...")
        
        # .env 파일에 새 토큰 저장
        env_path = ".env"
        set_key(env_path, "TW_OAUTH2_ACCESS_TOKEN", new_token['access_token'])
        
        # 새로운 refresh token이 있으면 업데이트
        if 'refresh_token' in new_token:
            set_key(env_path, "TW_OAUTH2_REFRESH_TOKEN", new_token['refresh_token'])
            print(f"New Refresh Token: {new_token['refresh_token'][:20]}...")
        
        print(f"\n새 토큰이 {env_path} 파일에 저장되었습니다.\n")
        
        return new_token
        
    except Exception as e:
        print(f"[ERROR] 토큰 갱신 실패: {e}", file=sys.stderr)
        print("Refresh Token이 만료되었거나 유효하지 않습니다.", file=sys.stderr)
        print("oauth2_setup.py를 실행하여 새로운 인증을 받으세요.\n", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

def setup_oauth2():
    """OAuth 2.0 인증 Flow 실행"""
    global auth_code, auth_error
    
    client_id, client_secret = load_credentials()
    
    print("OAuth 2.0 User Context 인증을 시작합니다...\n")
    
    # 로컬 서버 시작
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server_thread = threading.Thread(target=server.handle_request)
    server_thread.daemon = True
    server_thread.start()
    print("✓ 로컬 서버가 http://localhost:8080 에서 대기 중...\n")
    
    # OAuth2UserHandler 생성
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=client_id,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        client_secret=client_secret
    )
    
    # Authorization URL 생성
    auth_url = oauth2_user_handler.get_authorization_url()
    
    print("1. 브라우저가 열립니다. Twitter 로그인 후 앱을 승인하세요.")
    print("2. 승인하면 자동으로 인증 코드를 받습니다.")
    print(f"\n수동으로 열려면: {auth_url}\n")
    
    # 브라우저 열기
    webbrowser.open(auth_url)
    
    print("브라우저에서 앱을 승인해주세요...\n")
    
    # 서버가 callback을 받을 때까지 대기
    server_thread.join(timeout=30)  # 30초 대기
    
    if auth_error:
        print(f"[ERROR] 인증 실패: {auth_error}", file=sys.stderr)
        sys.exit(1)
    
    if not auth_code:
        print("[WARN] 자동으로 인증 코드를 받지 못했습니다.")
        print("브라우저의 callback URL 전체를 붙여넣으세요.\n")
        
        auth_code = input("Callback URL: ").strip()
        
        # URL 검증
        try:
            parsed = urlparse(auth_code)
            params = parse_qs(parsed.query)
            if 'code' not in params:
                print("[ERROR] URL에서 'code' 파라미터를 찾을 수 없습니다.", file=sys.stderr)
                sys.exit(1)
            print(f"✓ 코드를 추출했습니다.\n")
        except Exception as e:
            print(f"[ERROR] URL 파싱 실패: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("✓ 인증 코드를 받았습니다!\n")
    
    # Access Token 발급
    try:
        access_token = oauth2_user_handler.fetch_token(auth_code)
        
        print("✅ 인증 성공!")
        print(f"Access Token: {access_token['access_token'][:20]}...")
        
        if 'refresh_token' in access_token:
            print(f"Refresh Token: {access_token['refresh_token'][:20]}...")
        
        # .env 파일에 저장
        env_path = ".env"
        set_key(env_path, "TW_OAUTH2_ACCESS_TOKEN", access_token['access_token'])
        
        if 'refresh_token' in access_token:
            set_key(env_path, "TW_OAUTH2_REFRESH_TOKEN", access_token['refresh_token'])
        
        print(f"\n토큰이 {env_path} 파일에 저장되었습니다.")
        print("이제 test.py를 실행할 수 있습니다!\n")
        
    except Exception as e:
        print(f"[ERROR] 토큰 발급 실패: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Twitter OAuth 2.0 설정")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh Token을 사용해서 Access Token 갱신"
    )
    
    args = parser.parse_args()
    
    if args.refresh:
        refresh_access_token()
    else:
        setup_oauth2()

