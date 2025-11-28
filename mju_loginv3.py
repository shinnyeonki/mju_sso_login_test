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

# 1. 환경변수 로드
load_dotenv()
# .strip()을 추가하여 혹시 모를 공백 제거
USER_ID = os.getenv('MJU_ID', '').strip()
USER_PW = os.getenv('MJU_PW', '').strip()

if not USER_ID or not USER_PW:
    print("Error: .env 파일 설정을 확인해주세요.")
    exit()

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://sso.mju.ac.kr/'
})

def get_random_string(length=32):
    # 특수문자 제외, 영문 대소문자+숫자만 사용 (JS Math.random() 대응)
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def login_mju_sso_v3(user_id, user_pw):
    # --- [Step 1] 접속 ---
    login_url = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp"
    res = session.get(login_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    try:
        public_key_str = soup.find('input', {'id': 'public-key'}).get('value')
        csrf_token = soup.find('input', {'id': 'c_r_t'}).get('value')
        form_action = soup.find('form', {'id': 'signin-form'}).get('action')
        
        if form_action.startswith("/"):
            action_url = "https://sso.mju.ac.kr" + form_action
        else:
            action_url = form_action
            
    except AttributeError:
        print(">>> [오류] 로그인 폼을 찾을 수 없습니다.")
        return False

    # --- [Step 2] 암호화 (Standard Bandi Logic) ---
    session_key_str = get_random_string(32)
    current_time = str(int(time.time() * 1000)) 

    # 2-1. RSA 암호화 (키 + 시간)
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    rsa_key = RSA.import_key(pem_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    rsa_payload = (session_key_str + "," + current_time).encode('utf-8')
    encsymka = base64.b64encode(cipher_rsa.encrypt(rsa_payload)).decode('utf-8')

    # 2-2. AES 암호화 (비밀번호)
    # [복구] IV를 다시 Null Bytes(0x00)로 설정. 
    # V2의 실패 원인이 IV 불일치로 인한 패스워드 깨짐일 확률이 높음.
    key_bytes = session_key_str.encode('utf-8')
    iv = b'\x00' * 16 
    
    cipher_aes = AES.new(key_bytes, AES.MODE_CBC, iv)
    padded_pw = pad(user_pw.encode('utf-8'), AES.block_size)
    enc_pw = base64.b64encode(cipher_aes.encrypt(padded_pw)).decode('utf-8')

    # --- [Step 3] 전송 ---
    payload = {
        'user_id': user_id,
        'pw_enc': enc_pw,
        'encsymka': encsymka,
        'c_r_t': csrf_token,
        'remember-me': 'on',
        'alk_id': '',      # 필수값일 수 있어 빈값 명시
        'alk_id_enc': ''   # 필수값일 수 있어 빈값 명시
    }

    print(f">>> [전송] ID: {user_id} / 로그인 시도 중...")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://sso.mju.ac.kr',
        'Referer': login_url
    }
    
    login_res = session.post(action_url, data=payload, headers=headers)
    
    # --- [Step 4] 결과 확인 ---
    # URL에 물음표(?) 앞부분만 잘라서 도메인 확인
    current_url_base = login_res.url.split('?')[0]
    
    if "lms.mju.ac.kr" in current_url_base:
        print("\n>>> [성공] LMS 로그인 완료!")
        print(f"최종 URL: {login_res.url}")
        return True
    
    # 실패 메시지 디코딩하여 출력
    print(f"\n>>> [실패] 로그인되지 않음. (URL: {login_res.url})")
    
    alert_match = re.search(r"alert\(['\"](.*?)['\"]\)", login_res.text)
    js_var_match = re.search(r'var errorMsg = ["\'](.*?)["\'];', login_res.text)
    
    msg = ""
    if alert_match:
        msg = alert_match.group(1)
    elif js_var_match:
        msg = js_var_match.group(1)
        
    # 유니코드(\u...)가 섞여있을 수 있으므로 디코딩 시도
    if msg:
        try:
            print(f"서버 메시지: {msg.encode('utf-8').decode('unicode_escape')}")
        except:
            print(f"서버 메시지(Raw): {msg}")
    else:
        print("서버 에러 메시지를 찾을 수 없습니다.")
        
    return False

if __name__ == "__main__":
    if login_mju_sso_v3(USER_ID, USER_PW):
        print("\n[세션 쿠키 확인]")
        print(session.cookies.get_dict())