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

from .utils import get_logger


# 모듈 로거
logger = get_logger(__name__)


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


def encrypt_with_rsa(data: str, public_key_str: str) -> str:
    """
    RSA-PKCS1-v1.5로 데이터 암호화 (JavaScript bandiJS.encryptJavaPKI 대응)
    
    Args:
        data: 암호화할 데이터 (예: "keyStr,타임스탬프")
        public_key_str: Base64로 인코딩된 RSA 공개키
    
    Returns:
        Base64로 인코딩된 암호문
    """
    logger.debug("[RSA 암호화 과정]")
    logger.debug(f"Input Data: {data[:30]}..." if len(data) > 30 else f"Input Data: {data}")
    
    # PEM 형식으로 변환
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    
    # RSA 키 로드
    rsa_key = RSA.import_key(pem_key)
    
    logger.debug(f"RSA Key Size: {rsa_key.size_in_bits()} bits")
    
    # PKCS1_v1_5 암호화 (Java 호환)
    cipher = PKCS1_v1_5.new(rsa_key)
    encrypted = cipher.encrypt(data.encode('utf-8'))
    result = base64.b64encode(encrypted).decode('utf-8')
    
    logger.debug(f"Encrypted (RSA): {result[:30]}...({len(result)} chars)")
    
    return result


def encrypt_with_aes(plain_text: str, key_info: dict) -> str:
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
    
    Returns:
        Base64로 인코딩된 암호문
    """
    logger.debug("[AES 암호화 과정]")
    
    key_bytes = key_info['key']
    iv_bytes = key_info['iv']
    
    logger.debug(f"AES Key: PBKDF2 derived ({len(key_bytes)} bytes)")
    logger.debug(f"IV: last 16 bytes of key ({len(iv_bytes)} bytes)")
    
    # 평문을 먼저 Base64 인코딩 (JS와 동일)
    input_data = base64.b64encode(plain_text.encode('utf-8'))
    
    logger.debug(f"Pre-encoded (Base64): {input_data[:20]}...")
    
    # AES-CBC 암호화
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded = pad(input_data, AES.block_size)
    encrypted = cipher.encrypt(padded)
    
    result = base64.b64encode(encrypted).decode('utf-8')
    
    logger.debug(f"Encrypted (AES): {result[:30]}...({len(result)} chars)")
    
    return result
