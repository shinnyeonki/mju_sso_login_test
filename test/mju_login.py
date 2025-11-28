import os
import time
import base64
import random
import string
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 암호화 라이브러리
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Util.Padding import pad

# 환경변수 로드
load_dotenv()
USER_ID = os.getenv('MJU_ID')
USER_PW = os.getenv('MJU_PW')

# 세션 설정
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://sso.mju.ac.kr/'
})

def get_random_string(length=32):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def print_log(step, msg):
    print(f"[{step}] {msg}")

def login_mju_sso_debug(user_id, user_pw):
    # 1. 로그인 페이지 접속
    login_url = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp"
    res = session.get(login_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    print_log("INIT", f"초기 페이지 접근 완료 (Status: {res.status_code})")

    # Hidden 필드 추출
    try:
        public_key_str = soup.find('input', {'id': 'public-key'}).get('value')
        csrf_token = soup.find('input', {'id': 'c_r_t'}).get('value')
        form_action = soup.find('form', {'id': 'signin-form'}).get('action')
        action_url = "https://sso.mju.ac.kr" + form_action
    except AttributeError:
        print_log("ERROR", "로그인 폼을 찾을 수 없습니다. IP 차단이나 페이지 구조 변경 확인 필요.")
        return False

    # 2. 암호화 (JS 로직 재현)
    session_key_str = get_random_string(32)
    current_time = str(int(time.time() * 1000))
    
    # 2-1. RSA (encsymka)
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    rsa_key = RSA.import_key(pem_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    rsa_payload = (session_key_str + "," + current_time).encode('utf-8')
    encsymka = base64.b64encode(cipher_rsa.encrypt(rsa_payload)).decode('utf-8')

    # 2-2. AES (pw_enc) - 명지대 Bandi 라이브러리 특성상 IV 확인 중요
    # 보통 IV를 Null(0x00)로 쓰거나 Key의 앞부분을 씁니다. 일단 Null로 시도.
    iv = b'\x00' * 16
    key_bytes = session_key_str.encode('utf-8')
    cipher_aes = AES.new(key_bytes, AES.MODE_CBC, iv)
    padded_pw = pad(user_pw.encode('utf-8'), AES.block_size)
    enc_pw = base64.b64encode(cipher_aes.encrypt(padded_pw)).decode('utf-8')

    payload = {
        'user_id': user_id,
        'pw': '',
        'pw_enc': enc_pw,
        'encsymka': encsymka,
        'c_r_t': csrf_token,
        'user_id_enc': '',
        'remember-me': 'on'
    }

    print_log("SEND", f"로그인 데이터 전송 중... (Target: {action_url})")
    
    # 3. POST 전송
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://sso.mju.ac.kr',
        'Upgrade-Insecure-Requests': '1'
    }
    
    login_res = session.post(action_url, data=payload, headers=headers)

    # 4. 결과 정밀 분석
    print_log("RESULT", "--------------------------------------------------")
    print_log("RESULT", f"응답 코드: {login_res.status_code}")
    print_log("RESULT", f"현재 URL : {login_res.url}")
    
    # 리다이렉트 내역 확인
    if login_res.history:
        print_log("DEBUG", "리다이렉트 경로:")
        for resp in login_res.history:
            print(f"         -> {resp.status_code} : {resp.url}")
    else:
        print_log("DEBUG", "리다이렉트 발생 안 함 (로그인 실패 가능성 높음)")

    # 5. 실패 시 서버 메시지(Alert) 추출
    # 명지대 SSO는 실패 시 자바스크립트 alert()로 에러를 띄웁니다.
    if "sso.mju.ac.kr" in login_res.url:
        alert_match = re.search(r"alert\(['\"](.*?)['\"]\)", login_res.text)
        if alert_match:
            error_msg = alert_match.group(1).replace("\\n", " ")
            print_log("FAIL", f"서버 에러 메시지: [ {error_msg} ]")
        else:
            print_log("FAIL", "로그인 페이지에 머물러 있으나 에러 메시지를 찾을 수 없습니다.")
        return False
        
    # 6. 성공 판단 (URL 호스트가 변경되었는지 확인)
    if "lms.mju.ac.kr" in login_res.url:
        print_log("SUCCESS", "LMS 도메인 진입 확인!")
        return True
    
    return False

# 실행
if __name__ == "__main__":
    if login_mju_sso_debug(USER_ID, USER_PW):
        print("\n>>> LMS 로그인 검증")
        lms_res = session.get("https://lms.mju.ac.kr/ilos/main/main_form.acl")
        
        # LMS 로그인 여부는 '로그아웃' 버튼이 있는지로 확실히 알 수 있음
        if "로그아웃" in lms_res.text or "Logout" in lms_res.text:
            print(">>> [최종 성공] LMS 메인 페이지에서 로그아웃 버튼을 찾았습니다.")
        else:
            print(">>> [불완전] LMS 페이지엔 접속했으나 로그인 세션이 확인되지 않습니다.")
    else:
        print("\n>>> [최종 실패] 로그인을 완료하지 못했습니다.")