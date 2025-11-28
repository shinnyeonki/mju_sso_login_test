"""
암호화 유틸리티
===============
RSA/AES 하이브리드 암호화 구현 (명지대 SSO 호환)

JavaScript 원본 (bandiJS):
- genKey(length): 세션키 생성 + PBKDF2로 AES 키 파생
- encryptJavaPKI(data): RSA로 암호화
- encryptBase64AES(data, keyInfo): AES로 암호화
"""

import base64
import random

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA1

from .utils import Colors, log_info


def generate_session_key(length: int = 32) -> dict:
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
    # 64바이트 랜덤 데이터를 Base64로 인코딩 (JS: forge.util.encode64(forge.random.getBytesSync(64)))
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
        hmac_hash_module=SHA1  # forge.pkcs5.pbkdf2 기본값은 SHA1
    )
    
    # IV = 키의 마지막 16바이트
    iv_bytes = key_bytes[-16:]
    
    return {
        'keyStr': key_str,
        'key': key_bytes,
        'iv': iv_bytes
    }


def encrypt_with_rsa(data: str, public_key_str: str, verbose: bool = False) -> str:
    """
    RSA-PKCS1-v1.5로 데이터 암호화 (JavaScript bandiJS.encryptJavaPKI 대응)
    
    Args:
        data: 암호화할 데이터 (예: "keyStr,타임스탬프")
        public_key_str: Base64로 인코딩된 RSA 공개키
        verbose: 상세 로그 출력 여부
    
    Returns:
        Base64로 인코딩된 암호문
    """
    if verbose:
        print(f"\n{Colors.CYAN}    [RSA 암호화 과정]{Colors.END}")
        log_info("Input Data", f"{data[:30]}..." if len(data) > 30 else data, 6)
    
    # PEM 형식으로 변환
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    
    # RSA 키 로드
    rsa_key = RSA.import_key(pem_key)
    
    if verbose:
        log_info("RSA Key Size", f"{rsa_key.size_in_bits()} bits", 6)
    
    # PKCS1_v1_5 암호화 (Java 호환)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted = cipher.encrypt(data.encode('utf-8'))
    result = base64.b64encode(encrypted).decode('utf-8')
    
    if verbose:
        log_info("Encrypted (RSA)", f"{result[:30]}...({len(result)} chars)", 6)
    
    return result


def encrypt_with_aes(plain_text: str, key_info: dict, verbose: bool = False) -> str:
    """
    AES-256-CBC로 데이터 암호화 (JavaScript bandiJS.encryptBase64AES 대응)
    
    JavaScript 원본:
    ```javascript
    encryptBase64AES: function(value, keyInfo, isEncodeUri, isUtf8) {
        var encValue = value;
        // ASCII 문자인 경우
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
        verbose: 상세 로그 출력 여부
    
    Returns:
        Base64로 인코딩된 암호문
    """
    if verbose:
        print(f"\n{Colors.CYAN}    [AES 암호화 과정]{Colors.END}")
    
    key_bytes = key_info['key']
    iv_bytes = key_info['iv']
    
    if verbose:
        log_info("AES Key", f"PBKDF2 derived ({len(key_bytes)} bytes)", 6)
        log_info("IV", f"last 16 bytes of key ({len(iv_bytes)} bytes)", 6)
    
    # 평문을 먼저 Base64 인코딩 (JS와 동일)
    input_data = base64.b64encode(plain_text.encode('utf-8'))
    
    if verbose:
        log_info("Pre-encoded (Base64)", f"{input_data[:20]}...", 6)
    
    # AES-CBC 암호화
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded = pad(input_data, AES.block_size)
    encrypted = cipher.encrypt(padded)
    
    result = base64.b64encode(encrypted).decode('utf-8')
    
    if verbose:
        log_info("Encrypted (AES)", f"{result[:30]}...({len(result)} chars)", 6)
    
    return result
