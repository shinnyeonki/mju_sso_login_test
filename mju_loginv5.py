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
# 공백 제거 및 환경변수 확인
USER_ID = os.getenv('MJU_ID', '').strip()
USER_PW = os.getenv('MJU_PW', '').strip()

# [중요] 아이디/비번 로드 확인 (앞 2글자만 출력)
if len(USER_ID) > 2 and len(USER_PW) > 2:
    print(f"Loaded ID: {USER_ID[:2]}**** / PW: {USER_PW[:2]}****")
else:
    print("Error: .env 파일이 제대로 로드되지 않았습니다.")
    exit()

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://sso.mju.ac.kr/'
})

def get_random_string(length=32):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def encrypt_aes_prepend_iv(plain_text, session_key_str):
    """
    [핵심 수정]
    IV를 랜덤으로 생성하고, 암호문 앞에 붙여서 Base64로 인코딩합니다.
    Format: Base64( IV(16bytes) + EncryptedBytes )
    """
    # 1. 키 준비
    key_bytes = session_key_str.encode('utf-8')
    
    # 2. 랜덤 IV 생성 (16 bytes)
    iv = os.urandom(16)
    
    # 3. 암호화
    cipher_aes = AES.new(key_bytes, AES.MODE_CBC, iv)
    padded_txt = pad(plain_text.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher_aes.encrypt(padded_txt)
    
    # 4. 결합 (IV + 암호문) 및 인코딩
    final_payload = iv + encrypted_bytes
    return base64.b64encode(final_payload).decode('utf-8')

def login_mju_sso_v5(user_id, user_pw):
    # 1. 접속
    login_url = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp"
    res = session.get(login_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    try:
        public_key_str = soup.find('input', {'id': 'public-key'}).get('value')
        csrf_token = soup.find('input', {'id': 'c_r_t'}).get('value')
        form_action = soup.find('form', {'id': 'signin-form'}).get('action')
        action_url = "https://sso.mju.ac.kr" + form_action if form_action.startswith("/") else form_action
    except AttributeError:
        print(">>> [오류] 폼 요소를 찾을 수 없습니다.")
        return False

    # 2. 암호화
    session_key_str = get_random_string(32)
    current_time = str(int(time.time() * 1000)) 

    # 2-1. RSA (Key)
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    rsa_key = RSA.import_key(pem_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    rsa_payload = (session_key_str + "," + current_time).encode('utf-8')
    encsymka = base64.b64encode(cipher_rsa.encrypt(rsa_payload)).decode('utf-8')

    # 2-2. AES (PW) - V5 방식 (Prepend IV)
    enc_pw = encrypt_aes_prepend_iv(user_pw, session_key_str)
    
    # 2-3. AES (Hidden Field)
    enc_alk_id = encrypt_aes_prepend_iv("", session_key_str)

    # 3. 전송
    payload = {
        'user_id': user_id,
        'pw': '',
        'pw_enc': enc_pw,
        'encsymka': encsymka,
        'c_r_t': csrf_token,
        'remember-me': 'on',
        'alk_id': '',
        'alk_id_enc': enc_alk_id,
        'user_id_enc': '' 
    }

    print(f">>> [전송] V5 방식(IV+Data)으로 로그인 시도...")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://sso.mju.ac.kr',
        'Referer': login_url
    }
    
    login_res = session.post(action_url, data=payload, headers=headers)
    
    # 4. 결과 확인
    current_url_base = login_res.url.split('?')[0]
    if "lms.mju.ac.kr" in current_url_base:
        print("\n>>> [성공] ★★★ LMS 로그인 성공! ★★★")
        print(f"최종 URL: {login_res.url}")
        return True
    
    print(f"\n>>> [실패] 이동 안함.")
    # 에러 메시지 추출
    try:
        if 'alert' in login_res.text:
            msg = re.search(r"alert\(['\"](.*?)['\"]\)", login_res.text).group(1)
            print(f"Alert: {msg.encode('utf-8').decode('unicode_escape')}")
        elif 'var errorMsg' in login_res.text:
            msg = re.search(r'var errorMsg = ["\'](.*?)["\'];', login_res.text).group(1)
            print(f"ErrorMsg: {msg}")
    except:
        print("에러 메시지 파싱 불가")
        
    return False

if __name__ == "__main__":
    if login_mju_sso_v5(USER_ID, USER_PW):
        print(session.cookies.get_dict())