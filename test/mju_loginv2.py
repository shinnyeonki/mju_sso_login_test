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

load_dotenv()
USER_ID = os.getenv('MJU_ID')
USER_PW = os.getenv('MJU_PW')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://sso.mju.ac.kr/'
})

def get_random_string(length=32):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def login_mju_sso_final(user_id, user_pw):
    # 1. 페이지 접속
    login_url = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp"
    res = session.get(login_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    try:
        public_key_str = soup.find('input', {'id': 'public-key'}).get('value')
        csrf_token = soup.find('input', {'id': 'c_r_t'}).get('value')
        form_action = soup.find('form', {'id': 'signin-form'}).get('action')
        # Action URL에 도메인이 없으면 붙여줌
        if form_action.startswith("/"):
            action_url = "https://sso.mju.ac.kr" + form_action
        else:
            action_url = form_action
            
        print(f">>> [준비] Action URL: {action_url}")
        
    except AttributeError:
        print(">>> [오류] 로그인 폼을 찾을 수 없습니다.")
        return False

    # 2. 암호화 수행
    session_key_str = get_random_string(32)
    # Java Timestamp (ms)
    current_time = str(int(time.time() * 1000)) 

    # 2-1. RSA (Key Enc)
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    rsa_key = RSA.import_key(pem_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    rsa_payload = (session_key_str + "," + current_time).encode('utf-8')
    encsymka = base64.b64encode(cipher_rsa.encrypt(rsa_payload)).decode('utf-8')

    # 2-2. AES (Password Enc) - *** 핵심 수정 부분 ***
    key_bytes = session_key_str.encode('utf-8') # 32 bytes
    
    # [수정 1] IV를 키의 앞 16바이트 (Bandi/Forge 일반적 설정)
    iv = key_bytes[:16] 
    
    cipher_aes = AES.new(key_bytes, AES.MODE_CBC, iv)
    # PKCS7 Padding
    padded_pw = pad(user_pw.encode('utf-8'), AES.block_size)
    enc_pw = base64.b64encode(cipher_aes.encrypt(padded_pw)).decode('utf-8')

    # 3. Payload 구성
    payload = {
        'user_id': user_id,
        'pw_enc': enc_pw,  # 암호화된 비번
        'encsymka': encsymka,
        'c_r_t': csrf_token,
        'remember-me': 'on'
    }

    print(">>> [전송] 로그인 시도 중...")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://sso.mju.ac.kr',
        'Referer': login_url  # Referer를 정확하게 로그인 페이지로 지정
    }
    
    # 4. POST 요청
    login_res = session.post(action_url, data=payload, headers=headers)
    
    # 5. 결과 분석
    # 수정 제안: 도메인 자체가 바뀌었는지 확인해야 함
    if "lms.mju.ac.kr" in login_res.url.split('?')[0]: # 물음표 앞부분(도메인+경로)만 검사
        print("성공")
    else:
        print("실패 (URL이 여전히 SSO 페이지임)")
    
    # 실패 원인 분석
    print(f">>> [실패] 페이지 이동 없음. (URL: {login_res.url})")
    
    # 5-1. alert() 메시지 찾기
    alert_match = re.search(r"alert\(['\"](.*?)['\"]\)", login_res.text)
    
    # 5-2. var errorMsg 변수 찾기 (제공해주신 JS 코드 기반)
    # var errorMsg = "아이디 또는 비밀번호가..."; 
    js_var_match = re.search(r'var errorMsg = ["\'](.*?)["\'];', login_res.text)
    
    if alert_match:
        print(f"서버 메시지(Alert): {alert_match.group(1)}")
    elif js_var_match:
        print(f"서버 메시지(Var): {js_var_match.group(1)}")
    else:
        # 5-3. 페이지 소스 일부 출력 (디버깅용)
        print("에러 메시지를 찾을 수 없습니다. HTML 일부:")
        # input value가 유지되었는지 확인 (보통 실패하면 input이 비워짐)
        if 'value="' + user_id + '"' in login_res.text:
             print("- 아이디 입력값은 유지됨")
        else:
             print("- 폼이 완전히 초기화됨 (세션 만료 또는 암호화 데이터 포맷 오류)")
             
    return False

if __name__ == "__main__":
    if login_mju_sso_final(USER_ID, USER_PW):
        # 쿠키 확인
        print("\n획득한 쿠키:")
        print(session.cookies.get_dict())