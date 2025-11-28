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
# 공백 제거는 필수입니다.
USER_ID = os.getenv('MJU_ID', '').strip()
USER_PW = os.getenv('MJU_PW', '').strip()

if not USER_ID or not USER_PW:
    print("Error: .env 파일에 아이디/비밀번호가 비어있습니다.")
    exit()

session = requests.Session()
# 헤더를 실제 브라우저와 동일하게 맞춤
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://sso.mju.ac.kr/'
})

def get_random_string(length=32):
    # BandiJS genKey 대응 (영문대소문자+숫자)
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def encrypt_aes(plain_text, session_key_str):
    """BandiJS encryptBase64AES 대응 함수"""
    # 1. 키 준비 (32 bytes)
    key_bytes = session_key_str.encode('utf-8')
    
    # 2. IV 준비 (키의 앞 16자리 - V2 방식)
    iv = key_bytes[:16]
    
    # 3. 암호화 (AES-256-CBC, PKCS7 Padding)
    cipher_aes = AES.new(key_bytes, AES.MODE_CBC, iv)
    
    # 4. 데이터 인코딩 (utf-8)
    # plain_text가 빈 문자열이어도 패딩 후 암호화해야 함
    padded_txt = pad(plain_text.encode('utf-8'), AES.block_size)
    
    # 5. Base64 인코딩
    return base64.b64encode(cipher_aes.encrypt(padded_txt)).decode('utf-8')

def login_mju_sso_final_v4(user_id, user_pw):
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
        print(">>> [오류] 페이지 로드 실패. (IP 차단 확인 필요)")
        return False

    # --- [Step 2] 암호화 수행 ---
    # 2-1. 세션키 생성
    session_key_str = get_random_string(32)
    current_time = str(int(time.time() * 1000)) 

    # 2-2. RSA 암호화 (키 교환)
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    rsa_key = RSA.import_key(pem_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    rsa_payload = (session_key_str + "," + current_time).encode('utf-8')
    encsymka = base64.b64encode(cipher_rsa.encrypt(rsa_payload)).decode('utf-8')

    # 2-3. AES 암호화 (비밀번호) - V2 방식(IV=Key[:16]) 적용
    enc_pw = encrypt_aes(user_pw, session_key_str)
    
    # 2-4. AES 암호화 (추가 필드 alk_id) - 빈 값이라도 암호화해서 보내는 경우가 있음
    enc_alk_id = encrypt_aes("", session_key_str)

    # --- [Step 3] 전송 데이터 구성 ---
    payload = {
        'user_id': user_id,
        'pw': '',             # JS에서는 지워짐
        'pw_enc': enc_pw,
        'encsymka': encsymka,
        'c_r_t': csrf_token,
        'remember-me': 'on',
        
        # HTML 폼에는 없지만 JS 로직에 존재하는 필드들 (혹시 몰라 추가)
        'alk_id': '',
        'alk_id_enc': enc_alk_id,
        'user_id_enc': '' 
    }

    # 헤더 강화 (Referer 필수)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://sso.mju.ac.kr',
        'Referer': login_url,
        'Upgrade-Insecure-Requests': '1'
    }

    print(f">>> [전송] ID: {user_id} 로그인 시도... (IV: Key[:16] 방식)")
    login_res = session.post(action_url, data=payload, headers=headers)
    
    # --- [Step 4] 결과 판별 ---
    # URL이 sso 도메인을 벗어나 lms로 바뀌었는지 확인 (가장 확실한 방법)
    current_url_base = login_res.url.split('?')[0]
    
    if "lms.mju.ac.kr" in current_url_base:
        print("\n>>> [성공] ★★★ LMS 로그인 성공! ★★★")
        print(f"최종 URL: {login_res.url}")
        return True
    
    # 실패 시 메시지 확인
    print(f"\n>>> [실패] URL 이동 안함.")
    alert_match = re.search(r"alert\(['\"](.*?)['\"]\)", login_res.text)
    js_var_match = re.search(r'var errorMsg = ["\'](.*?)["\'];', login_res.text)
    
    msg = ""
    if alert_match: msg = alert_match.group(1)
    elif js_var_match: msg = js_var_match.group(1)
    
    if msg:
        # 유니코드 디코딩 처리
        try:
            print(f"서버 응답: {msg.encode('utf-8').decode('unicode_escape')}")
        except:
            print(f"서버 응답(Raw): {msg}")
    else:
        print("서버 응답 메시지 없음 (폼 초기화됨)")
        
    return False

if __name__ == "__main__":
    if login_mju_sso_final_v4(USER_ID, USER_PW):
        print("\n[세션 정보]")
        print(session.cookies.get_dict())