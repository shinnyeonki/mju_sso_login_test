"""
명지대학교 SSO 로그인 모듈
==========================
하이브리드 암호화 (RSA + AES) 방식을 사용한 SSO 로그인 구현

작동 원리:
1. GET 요청으로 로그인 페이지 접속 → 공개키, CSRF 토큰, 세션 쿠키 획득
2. 클라이언트에서 세션키 생성 후 RSA로 암호화 (키 교환)
3. 비밀번호를 세션키로 AES 암호화
4. POST 요청으로 암호화된 데이터 전송
5. 성공 시 리다이렉트 URL로 이동
"""

import os
import time
import base64
import random
import string
import re
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from dotenv import load_dotenv

# 암호화 라이브러리
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1

# ========================================
# 로깅 유틸리티
# ========================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_section(title):
    """섹션 구분선 출력"""
    print(f"\n{Colors.HEADER}{'='*70}")
    print(f" {title}")
    print(f"{'='*70}{Colors.END}\n")

def log_step(step_num, title):
    """단계 출력"""
    print(f"{Colors.BOLD}{Colors.BLUE}[Step {step_num}] {title}{Colors.END}")

def log_info(label, value, indent=2):
    """정보 출력"""
    spaces = ' ' * indent
    if isinstance(value, dict):
        print(f"{spaces}{Colors.CYAN}{label}:{Colors.END}")
        for k, v in value.items():
            # 민감 정보 마스킹
            if 'password' in k.lower() or 'pw' in k.lower():
                v = '****' if v else '(empty)'
            print(f"{spaces}  {k}: {v}")
    elif isinstance(value, str) and len(value) > 100:
        print(f"{spaces}{Colors.CYAN}{label}:{Colors.END} {value[:50]}...({len(value)} chars)")
    else:
        print(f"{spaces}{Colors.CYAN}{label}:{Colors.END} {value}")

def log_success(message):
    """성공 메시지"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def log_error(message):
    """에러 메시지"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def log_warning(message):
    """경고 메시지"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def log_request(method, url, headers=None, data=None):
    """HTTP 요청 로깅"""
    print(f"\n{Colors.YELLOW}>>> {method} Request >>>{Colors.END}")
    log_info("URL", url)
    if headers:
        important_headers = {k: v for k, v in headers.items() 
                          if k.lower() in ['content-type', 'origin', 'referer', 'cookie']}
        if important_headers:
            log_info("Headers", important_headers)
    if data:
        safe_data = {k: ('****' if 'pw' in k.lower() and v else v) for k, v in data.items()}
        log_info("Form Data", safe_data)

def log_response(response, show_body=True, max_body_length=5000):
    """HTTP 응답 로깅"""
    print(f"\n{Colors.YELLOW}<<< Response <<<{Colors.END}")
    log_info("Status Code", response.status_code)
    log_info("Final URL", response.url)
    
    # 전체 응답 헤더 출력
    print(f"\n  {Colors.CYAN}[Response Headers]{Colors.END}")
    for header_name, header_value in response.headers.items():
        log_info(header_name, header_value, 4)
    
    # 쿠키 출력
    if response.cookies:
        print(f"\n  {Colors.CYAN}[Response Cookies]{Colors.END}")
        log_info("Cookies", dict(response.cookies), 4)
    
    # 응답 본문 출력
    if show_body:
        print(f"\n  {Colors.CYAN}[Response Body]{Colors.END}")
        body = response.text
        if len(body) > max_body_length:
            print(f"    (총 {len(body)} chars, 처음 {max_body_length}자만 표시)")
            print(f"    {'-'*60}")
            print(body[:max_body_length])
            print(f"    ... (생략됨)")
        else:
            print(f"    {'-'*60}")
            print(body)
        print(f"    {'-'*60}")


# ========================================
# 암호화 유틸리티
# ========================================

def generate_session_key(length=32):
    """
    세션키 생성 (JavaScript bandiJS.genKey 대응)
    
    JavaScript 원본:
    ```javascript
    genKey: function(length) {
        var keyStr = forge.util.encode64(forge.random.getBytesSync(64));
        var salt = keyStr.substring(keyStr.length - 16);
        var keyBytes = forge.pkcs5.pbkdf2(keyStr, salt, 1024, length);
        var ivBytes = keyBytes.slice(keyBytes.length - 16);
        return { length, key: keyBytes, iv: ivBytes, keyStr };
    }
    ```
    
    Returns:
        dict: { 'keyStr': str, 'key': bytes, 'iv': bytes }
    """
    # 64바이트 랜덤 데이터를 Base64로 인코딩
    random_bytes = bytes(random.getrandbits(8) for _ in range(64))
    key_str = base64.b64encode(random_bytes).decode('utf-8')
    
    # salt = keyStr의 마지막 16자
    salt = key_str[-16:]
    
    # PBKDF2로 키 파생 (iterations=1024, dkLen=length)
    key_bytes = PBKDF2(
        password=key_str.encode('utf-8'),
        salt=salt.encode('utf-8'),
        dkLen=length,
        count=1024,
        hmac_hash_module=SHA1
    )
    
    # IV = 키의 마지막 16바이트
    iv_bytes = key_bytes[-16:]
    
    log_info("Generated Session Key (keyStr)", f"{key_str[:16]}...({len(key_str)} chars)", 4)
    
    return {
        'keyStr': key_str,
        'key': key_bytes,
        'iv': iv_bytes
    }


def encrypt_with_rsa(data: str, public_key_str: str) -> str:
    """
    RSA-PKCS1-v1.5로 데이터 암호화 (JavaScript bandiJS.encryptJavaPKI 대응)
    
    원리:
    - 서버의 공개키로 세션키+타임스탬프를 암호화
    - 서버만이 비밀키로 이를 복호화하여 세션키를 얻을 수 있음
    - PKCS1-v1.5 패딩 사용 (Java의 기본 RSA 패딩)
    
    Args:
        data: 암호화할 데이터 (예: "세션키,타임스탬프")
        public_key_str: Base64로 인코딩된 RSA 공개키
    
    Returns:
        Base64로 인코딩된 암호문
    """
    print(f"\n{Colors.CYAN}    [RSA 암호화 과정]{Colors.END}")
    log_info("Input Data", f"{data[:30]}..." if len(data) > 30 else data, 6)
    
    # PEM 형식으로 변환
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    
    # RSA 키 로드
    rsa_key = RSA.import_key(pem_key)
    log_info("RSA Key Size", f"{rsa_key.size_in_bits()} bits", 6)
    
    # PKCS1_v1_5 암호화 (Java 호환)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted = cipher.encrypt(data.encode('utf-8'))
    result = base64.b64encode(encrypted).decode('utf-8')
    
    log_info("Encrypted (RSA)", f"{result[:30]}...({len(result)} chars)", 6)
    return result


def encrypt_with_aes(plain_text: str, key_info: dict) -> str:
    """
    AES-256-CBC로 데이터 암호화 (JavaScript bandiJS.encryptBase64AES 대응)
    
    JavaScript 원본:
    ```javascript
    encryptBase64AES: function(value, keyInfo, isEncodeUri, isUtf8) {
        var encValue = value;
        var enc64Value = forge.util.encode64(encValue);  // Base64 인코딩
        var cipher = forge.cipher.createCipher('AES-CBC', keyInfo.key);
        cipher.start({iv: keyInfo.iv});
        cipher.update(forge.util.createBuffer(enc64Value));
        cipher.finish();
        return forge.util.encode64(cipher.output.bytes());
    }
    ```
    
    Args:
        plain_text: 암호화할 평문
        key_info: generate_session_key()에서 반환된 키 정보 dict
    
    Returns:
        Base64로 인코딩된 암호문
    """
    print(f"\n{Colors.CYAN}    [AES 암호화 과정]{Colors.END}")
    
    key_bytes = key_info['key']
    iv_bytes = key_info['iv']
    
    log_info("AES Key", f"PBKDF2 derived ({len(key_bytes)} bytes)", 6)
    log_info("IV", f"last 16 bytes of key ({len(iv_bytes)} bytes)", 6)
    
    # 평문을 먼저 Base64 인코딩 (JS와 동일)
    input_data = base64.b64encode(plain_text.encode('utf-8'))
    log_info("Pre-encoded (Base64)", f"{input_data[:20]}...", 6)
    
    # AES-256-CBC 암호화
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded = pad(input_data, AES.block_size)
    encrypted = cipher.encrypt(padded)
    
    result = base64.b64encode(encrypted).decode('utf-8')
    log_info("Encrypted (AES)", f"{result[:30]}...({len(result)} chars)", 6)
    
    return result


# ========================================
# MJU SSO 로그인 클래스
# ========================================

class MJUSSOLogin:
    """명지대학교 SSO 로그인 클래스"""
    
    # 서비스별 로그인 URL 설정
    SERVICES = {
        'lms': {
            'name': 'LMS (e-Class)',
            'url': 'https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp',
            'success_domain': 'lms.mju.ac.kr',
            'test_url': 'https://lms.mju.ac.kr/ilos/main/main_form.acl'
        },
        'portal': {
            'name': 'Portal (통합정보시스템)',
            'url': 'https://sso.mju.ac.kr/sso/auth?client_id=portal&response_type=code&state=1764321341781&rd_c_p=loginparam&tkn_type=normal&redirect_uri=https%3A%2F%2Fportal.mju.ac.kr%2Fsso%2Fresponse.jsp',
            'success_domain': 'portal.mju.ac.kr',
            'test_url': 'https://portal.mju.ac.kr/portal/main.do'
        },
        'library': {
            'name': 'Library (도서관)',
            'url': 'https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=library&state=state&redirect_uri=https://lib.mju.ac.kr/sso/login',
            'success_domain': 'lib.mju.ac.kr',
            'test_url': 'https://lib.mju.ac.kr/main'
        },
        'msi': {
            'name': 'MSI (통합정보)',
            'url': 'https://sso.mju.ac.kr/sso/auth?client_id=msi&response_type=code&state=1764322070097&tkn_type=normal&redirect_uri=https%3A%2F%2Fmsi.mju.ac.kr%2Findex_Myiweb.jsp',
            'success_domain': 'msi.mju.ac.kr',
            'test_url': 'https://msi.mju.ac.kr/index_Myiweb.jsp'
        },
        'myicap': {
            'name': 'MyiCAP (비교과)',
            'url': 'https://sso.mju.ac.kr/sso/auth?client_id=myicap&response_type=code&state=1764322418883&rd_c_p=loginparam&tkn_type=normal&redirect_uri=https%3A%2F%2Fmyicap.mju.ac.kr%2Findex.jsp',
            'success_domain': 'myicap.mju.ac.kr',
            'test_url': 'https://myicap.mju.ac.kr/index.jsp'
        }
    }
    
    def __init__(self, user_id: str, user_pw: str):
        """
        Args:
            user_id: 학번/교번
            user_pw: 비밀번호
        """
        self.user_id = user_id
        self.user_pw = user_pw
        
        # requests 세션 생성 (쿠키 자동 관리)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # 로그인 과정에서 획득한 데이터
        self.public_key = None
        self.csrf_token = None
        self.form_action = None
        
    def _parse_login_page(self, html: str) -> bool:
        """
        로그인 페이지에서 필요한 정보 추출
        
        추출 항목:
        1. public-key: RSA 공개키 (서버에서 발급)
        2. c_r_t: CSRF 토큰 (위조 방지)
        3. form action: POST 요청 URL
        """
        log_step("1-2", "로그인 페이지 파싱")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. 공개키 추출
        public_key_input = soup.find('input', {'id': 'public-key'})
        if not public_key_input:
            log_error("공개키(public-key)를 찾을 수 없습니다.")
            return False
        self.public_key = public_key_input.get('value')
        log_info("Public Key", self.public_key)
        print(f"      → 용도: 세션키를 RSA로 암호화하여 안전하게 서버로 전송")
        
        # 2. CSRF 토큰 추출
        csrf_input = soup.find('input', {'id': 'c_r_t'})
        if not csrf_input:
            log_error("CSRF 토큰(c_r_t)을 찾을 수 없습니다.")
            return False
        self.csrf_token = csrf_input.get('value')
        log_info("CSRF Token", self.csrf_token)
        print(f"      → 용도: Cross-Site Request Forgery 공격 방지")
        
        # 3. Form Action URL 추출
        form = soup.find('form', {'id': 'signin-form'})
        if not form:
            log_error("로그인 폼(signin-form)을 찾을 수 없습니다.")
            return False
        self.form_action = form.get('action')
        log_info("Form Action", self.form_action)
        
        # 추가 정보 추출
        jsessionid_match = re.search(r'jsessionid=([A-Z0-9]+)', self.form_action)
        if jsessionid_match:
            log_info("JSESSIONID (in URL)", jsessionid_match.group(1))
            print(f"      → 용도: 서버 세션 식별자 (URL Rewriting)")
        
        log_success("페이지 파싱 완료")
        return True
    
    def _prepare_encrypted_data(self) -> dict:
        """
        암호화된 로그인 데이터 준비
        
        암호화 과정:
        1. 32자리 랜덤 세션키 생성
        2. 세션키 + 타임스탬프를 RSA로 암호화 → encsymka
        3. 비밀번호를 세션키로 AES 암호화 → pw_enc
        """
        log_step("2", "암호화 데이터 준비")
        
        print(f"\n  {Colors.BOLD}[암호화 원리]{Colors.END}")
        print("  ┌─────────────────────────────────────────────────────────┐")
        print("  │ 1. 세션키 생성 (Client)                                    │")
        print("  │    └→ 매 로그인마다 새로운 32자리 랜덤 키 생성                   │")
        print("  │                                                         │")
        print("  │ 2. RSA 암호화 (키 교환)                                    │")
        print("  │    └→ '세션키,타임스탬프'를 서버 공개키로 암호화                  │")
        print("  │    └→ 서버만 비밀키로 복호화 가능                              │")
        print("  │                                                         │")
        print("  │ 3. AES 암호화 (데이터 보호)                                 │")
        print("  │    └→ 비밀번호를 세션키로 암호화                              │")
        print("  │    └→ 서버가 세션키를 복호화한 후에만 해독 가능                   │")
        print("  └─────────────────────────────────────────────────────────┘")
        
        # 1. 세션키 생성 (PBKDF2 파생 포함)
        print(f"\n  {Colors.CYAN}[1] 세션키 생성 (PBKDF2){Colors.END}")
        key_info = generate_session_key(32)
        
        # 2. 타임스탬프 생성
        timestamp = str(int(time.time() * 1000))
        log_info("Timestamp", timestamp, 4)
        print(f"      → 용도: 재전송 공격(Replay Attack) 방지")
        
        # 3. RSA 암호화 (keyStr + 타임스탬프) - keyStr을 서버로 전송
        print(f"\n  {Colors.CYAN}[2] RSA 암호화 (키 교환){Colors.END}")
        rsa_payload = f"{key_info['keyStr']},{timestamp}"
        log_info("RSA Payload", f"'{key_info['keyStr'][:16]}...,{timestamp}'", 4)
        encsymka = encrypt_with_rsa(rsa_payload, self.public_key)
        
        # 4. AES 암호화 (비밀번호) - PBKDF2로 파생된 key와 iv 사용
        print(f"\n  {Colors.CYAN}[3] AES 암호화 (비밀번호){Colors.END}")
        log_info("Password (Plain)", "****", 4)
        pw_enc = encrypt_with_aes(self.user_pw, key_info)
        
        log_success("암호화 완료")
        
        return {
            'user_id': self.user_id,
            'pw': '',  # 평문 비밀번호는 비움 (JS에서도 동일)
            'pw_enc': pw_enc,
            'encsymka': encsymka,
            'c_r_t': self.csrf_token,
            'user_id_enc': '',
        }
    
    def login(self, service: str = 'lms') -> dict:
        """
        SSO 로그인 수행
        
        Args:
            service: 로그인할 서비스 ('lms', 'portal', 'library')
        
        Returns:
            dict: 로그인 결과 {'success': bool, 'message': str, 'cookies': dict, 'final_url': str}
        """
        if service not in self.SERVICES:
            return {'success': False, 'message': f'Unknown service: {service}'}
        
        service_info = self.SERVICES[service]
        
        log_section(f"MJU SSO 로그인: {service_info['name']}")
        print(f"  User ID: {self.user_id[:4]}****")
        print(f"  Target: {service_info['url'][:60]}...")
        
        # ========================================
        # Step 1: 로그인 페이지 접속 (GET)
        # ========================================
        log_step("1-1", "로그인 페이지 접속 (GET)")
        print(f"\n  {Colors.BOLD}[요청 목적]{Colors.END}")
        print("  - 서버로부터 공개키(RSA)와 CSRF 토큰 획득")
        print("  - 세션 쿠키(JSESSIONID) 발급 받기")
        
        login_url = service_info['url']
        log_request('GET', login_url)
        
        try:
            response = self.session.get(login_url, timeout=10)
            log_response(response)
        except requests.RequestException as e:
            log_error(f"페이지 접속 실패: {e}")
            return {'success': False, 'message': str(e)}
        
        # 세션 쿠키 확인
        print(f"\n  {Colors.BOLD}[세션 쿠키 분석]{Colors.END}")
        for name, value in self.session.cookies.items():
            log_info(name, f"{value[:20]}..." if len(value) > 20 else value, 4)
            if name == 'JSESSIONID':
                print(f"      → 용도: 서버 세션 식별 (Tomcat)")
            elif name == 'bandisncdevid':
                print(f"      → 용도: 기기 식별 (보안 솔루션)")
        
        # 페이지 파싱
        if not self._parse_login_page(response.text):
            return {'success': False, 'message': '로그인 페이지 파싱 실패'}
        
        # ========================================
        # Step 2: 암호화 데이터 준비
        # ========================================
        encrypted_data = self._prepare_encrypted_data()
        
        # ========================================
        # Step 3: 로그인 요청 (POST)
        # ========================================
        log_step("3", "로그인 요청 전송 (POST)")
        
        print(f"\n  {Colors.BOLD}[요청 목적]{Colors.END}")
        print("  - 암호화된 인증 정보를 서버로 전송")
        print("  - 서버에서 복호화 후 인증 수행")
        print("  - 성공 시 Authorization Code와 함께 리다이렉트")
        
        # Form Action URL 처리
        if self.form_action.startswith('/'):
            action_url = f"https://sso.mju.ac.kr{self.form_action}"
        else:
            action_url = self.form_action
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://sso.mju.ac.kr',
            'Referer': login_url,
            'Upgrade-Insecure-Requests': '1',
        }
        
        log_request('POST', action_url, headers, encrypted_data)
        
        try:
            # allow_redirects=True: 리다이렉트 자동 따라가기
            response = self.session.post(
                action_url, 
                data=encrypted_data, 
                headers=headers,
                allow_redirects=True,
                timeout=15
            )
            log_response(response)
            
            # 응답 분석을 위한 추가 로깅
            print(f"\n  {Colors.BOLD}[응답 분석]{Colors.END}")
            
            # History 확인 (리다이렉트 체인)
            if response.history:
                print(f"    리다이렉트 체인:")
                for i, hist in enumerate(response.history):
                    log_info(f"  [{i+1}] {hist.status_code}", hist.url, 4)
            else:
                log_info("리다이렉트", "없음 (200 OK)", 4)
            
            # 응답 HTML에서 리다이렉트 URL 확인 (JavaScript redirect 등)
            js_redirect_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", response.text)
            meta_redirect_match = re.search(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\']+)["\']', response.text, re.IGNORECASE)
            
            # 폼에서 redirect_uri 파라미터 확인
            redirect_match = re.search(r'redirect_uri=([^&"\'>\s]+)', response.text)
            if redirect_match:
                redirect_uri = redirect_match.group(1)
                from urllib.parse import unquote
                redirect_uri = unquote(redirect_uri)
                log_info("Redirect URI (폼에서)", redirect_uri, 4)
            
            if js_redirect_match:
                redirect_url = js_redirect_match.group(1)
                log_info("JS Redirect URL 발견", redirect_url, 4)
                # JavaScript 리다이렉트 따라가기
                if redirect_url.startswith('http'):
                    print(f"    → JavaScript 리다이렉트 따라가기...")
                    response = self.session.get(redirect_url, allow_redirects=True, timeout=15)
                    log_response(response)
            elif meta_redirect_match:
                redirect_url = meta_redirect_match.group(1)
                log_info("Meta Redirect URL 발견", redirect_url, 4)
            
            # Authorization Code 확인 (URL에서)
            code_match = re.search(r'[?&]code=([^&]+)', response.url)
            if code_match:
                auth_code = code_match.group(1)
                log_info("Authorization Code", f"{auth_code[:20]}...", 4)
                print(f"      → OAuth2 인증 코드가 발급됨")
            
            # 로그인 성공 시 (에러가 없고 로그인 폼도 없음) 리다이렉트 시도
            if 'signin-form' not in response.text or '로그아웃' in response.text:
                # 폼의 action에서 redirect_uri를 추출하여 해당 URL로 이동
                redirect_uri_match = re.search(r'redirect_uri=([^&"\'>\s]+)', self.form_action)
                # service 정보에서 success_domain 가져오기
                service_info = self.SERVICES.get(service, {}) if isinstance(service, str) else service
                success_domain = service_info.get('success_check', {}).get('url_contains', '') if isinstance(service_info, dict) else ''
                if redirect_uri_match and success_domain and success_domain not in response.url:
                    from urllib.parse import unquote
                    target_redirect = unquote(redirect_uri_match.group(1))
                    print(f"\n  {Colors.YELLOW}→ 대상 서비스로 직접 접근 시도...{Colors.END}")
                    log_info("Target", target_redirect, 4)
                    
                    try:
                        redirect_response = self.session.get(target_redirect, allow_redirects=True, timeout=15)
                        if redirect_response.status_code == 200:
                            response = redirect_response
                            log_info("서비스 접근 결과", f"{redirect_response.status_code} - {redirect_response.url[:50]}...", 4)
                    except:
                        pass
                
        except requests.RequestException as e:
            log_error(f"로그인 요청 실패: {e}")
            return {'success': False, 'message': str(e)}
        
        # ========================================
        # Step 4: 결과 확인
        # ========================================
        log_step("4", "로그인 결과 확인")
        
        final_url = response.url
        success_domain = service_info['success_domain']
        
        # 응답 HTML 분석 - 로그인 성공 여부 확인
        # 로그인 실패 시 alert 메시지가 있음
        has_error = False
        error_msg = None
        
        # JavaScript alert 메시지 추출
        alert_match = re.search(r"alert\(['\"](.+?)['\"]\)", response.text)
        if alert_match:
            error_msg = alert_match.group(1)
            try:
                error_msg = error_msg.encode('utf-8').decode('unicode_escape')
            except:
                pass
            has_error = True
        
        # var errorMsg 추출
        if not error_msg:
            var_match = re.search(r'var errorMsg = ["\'](.+?)["\'];', response.text)
            if var_match:
                error_msg = var_match.group(1)
                has_error = True
        
        # 로그인 폼이 다시 나타났는지 확인 (실패 시 폼이 다시 표시됨)
        if 'signin-form' in response.text and 'input-password' in response.text:
            # 에러 메시지가 없어도 폼이 다시 나타나면 실패
            if not error_msg:
                has_error = True
                error_msg = "로그인 폼이 다시 표시됨 (인증 실패)"
        
        # 성공 판정: 최종 URL이 대상 도메인인지 확인 OR 로그인 폼이 없고 에러도 없음
        if success_domain in final_url:
            log_success(f"로그인 성공! ({service_info['name']})")
            
            print(f"\n  {Colors.BOLD}[인증 흐름 완료]{Colors.END}")
            print(f"  1. SSO 서버 인증 완료")
            print(f"  2. Authorization Code 발급됨")
            print(f"  3. {success_domain}으로 리다이렉트")
            print(f"  4. 서비스 세션 생성 완료")
            
            # 최종 쿠키 상태 (중복 쿠키 처리)
            print(f"\n  {Colors.BOLD}[최종 쿠키 상태]{Colors.END}")
            all_cookies = {}
            for cookie in self.session.cookies:
                key = f"{cookie.name}@{cookie.domain}"
                all_cookies[key] = cookie.value
            for name, value in all_cookies.items():
                log_info(name, f"{value[:30]}..." if len(value) > 30 else value, 4)
            
            return {
                'success': True,
                'message': '로그인 성공',
                'cookies': all_cookies,
                'final_url': final_url,
                'session': self.session
            }
        elif not has_error and '로그아웃' in response.text:
            # 로그아웃 버튼이 있으면 로그인 성공
            log_success(f"로그인 성공! ({service_info['name']})")
            
            # 최종 쿠키 상태
            print(f"\n  {Colors.BOLD}[최종 쿠키 상태]{Colors.END}")
            all_cookies = dict(self.session.cookies)
            for name, value in all_cookies.items():
                log_info(name, f"{value[:30]}..." if len(value) > 30 else value, 4)
            
            return {
                'success': True,
                'message': '로그인 성공',
                'cookies': all_cookies,
                'final_url': final_url,
                'session': self.session
            }
        else:
            # 실패 원인 분석
            log_error("로그인 실패")
            
            if error_msg:
                log_info("Server Error", error_msg, 4)
            else:
                log_info("Final URL", final_url, 4)
                
                # 2차 인증 필요 여부 확인
                if 'two-factor' in response.text.lower() or 'tf_val' in response.text:
                    log_warning("2차 인증(OTP)이 필요합니다.")
                    error_msg = "2차 인증 필요"
            
            return {
                'success': False,
                'message': error_msg or '알 수 없는 오류',
                'final_url': final_url
            }
    
    def test_session(self, test_url: str = None, service: str = 'lms') -> bool:
        """세션 유효성 테스트"""
        if not test_url:
            # 서비스별 테스트 URL 사용
            service_info = self.SERVICES.get(service, {})
            test_url = service_info.get('test_url', 'https://lms.mju.ac.kr/ilos/main/main_form.acl')
        
        log_step("5", "세션 유효성 테스트")
        log_info("Test URL", test_url)
        
        try:
            response = self.session.get(test_url, timeout=10, allow_redirects=True)
            
            log_info("응답 상태", response.status_code)
            log_info("최종 URL", response.url)
            
            # 리다이렉트 체인 확인
            if response.history:
                print(f"    리다이렉트 체인:")
                for i, hist in enumerate(response.history):
                    log_info(f"  [{i+1}] {hist.status_code}", hist.url, 4)
            
            # '로그아웃' 텍스트가 있으면 로그인 상태
            if '로그아웃' in response.text or 'Logout' in response.text or 'logout' in response.text.lower():
                log_success("세션 유효함 (로그인 상태 확인)")
                return True
            elif 'sso.mju.ac.kr' in response.url:
                log_warning("세션이 유효하지 않음 (SSO 로그인 페이지로 리다이렉트됨)")
                return False
            else:
                log_warning("세션 상태 불확실")
                return False
        except requests.RequestException as e:
            log_error(f"테스트 실패: {e}")
            return False


# ========================================
# 메인 실행
# ========================================

def main():
    """메인 함수"""
    
    print(f"""
{Colors.BOLD}{Colors.HEADER}
╔══════════════════════════════════════════════════════════════════════╗
║              명지대학교 SSO 로그인 테스트 프로그램                           ║
║                                                                      ║
║  이 프로그램은 SSO 로그인 과정을 상세히 분석하고 로깅합니다.                      ║
║  - 하이브리드 암호화 (RSA + AES)                                         ║
║  - OAuth2 Authorization Code Flow                                    ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.END}
""")
    
    # 환경변수 로드
    load_dotenv()
    user_id = os.getenv('MJU_ID', '').strip()
    user_pw = os.getenv('MJU_PW', '').strip()
    
    if not user_id or not user_pw:
        log_error(".env 파일에서 MJU_ID, MJU_PW를 찾을 수 없습니다.")
        print("\n.env 파일 형식:")
        print("  MJU_ID=학번")
        print("  MJU_PW=비밀번호")
        return
    
    log_info("Loaded User ID", f"{user_id[:4]}****")
    log_info("Loaded Password", "****")
    
    # 테스트할 서비스 목록
    services_to_test = ['lms', 'portal', 'msi', 'myicap']
    
    results = {}
    
    for service in services_to_test:
        # 각 서비스마다 새로운 세션으로 테스트
        sso = MJUSSOLogin(user_id, user_pw)
        result = sso.login(service)
        results[service] = result
        
        # 성공한 경우 세션 테스트
        if result['success']:
            sso.test_session(service=service)
        
        print("\n" + "─" * 70 + "\n")
    
    # ========================================
    # 최종 결과 요약
    # ========================================
    log_section("테스트 결과 요약")
    
    for service, result in results.items():
        service_name = MJUSSOLogin.SERVICES[service]['name']
        if result['success']:
            print(f"  {Colors.GREEN}✓ {service_name}: 성공{Colors.END}")
            print(f"    Final URL: {result['final_url'][:60]}...")
        else:
            print(f"  {Colors.RED}✗ {service_name}: 실패{Colors.END}")
            print(f"    원인: {result['message']}")
    
    print()


if __name__ == "__main__":
    main()
