# 명지대학교 SSO 로그인 프로세스 분석

> 이 문서는 명지대학교 SSO(Single Sign-On) 시스템의 로그인 흐름을 Client와 Server 관점에서 상세히 분석합니다.

---

## 목차
1. [개요](#1-개요)
2. [전체 흐름 다이어그램](#2-전체-흐름-다이어그램)
3. [1단계: 로그인 페이지 접속 (GET)](#3-1단계-로그인-페이지-접속-get)
4. [2단계: 로그인 요청 (POST)](#4-2단계-로그인-요청-post)
5. [3단계: 리다이렉트 처리](#5-3단계-리다이렉트-처리)
6. [암호화 상세](#6-암호화-상세)
7. [쿠키 및 세션 관리](#7-쿠키-및-세션-관리)
8. [에러 처리](#8-에러-처리)

---

## 1. 개요

### 1.1 시스템 정보
| 항목 | 값 |
|------|-----|
| SSO 도메인 | `sso.mju.ac.kr` |
| LMS 도메인 | `lms.mju.ac.kr` |
| 인증 방식 | OAuth2 Authorization Code Flow |
| 암호화 | 하이브리드 (RSA + AES) |
| 세션 관리 | JSESSIONID (Tomcat) |

### 1.2 사용 라이브러리 (Client-side JavaScript)
- `forge.min.js` - RSA/AES 암호화 라이브러리
- `bandi.lib.common.js` - 명지대 커스텀 암호화 유틸리티
- `jquery.cookie.js` - 쿠키 관리
- `sign.form.js` - 로그인 폼 처리

---

## 2. 전체 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MJU SSO Login Flow                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Client]                                [SSO Server]           [LMS Server]│
│     │                                         │                      │      │
│     │  1. GET /sso/auth?...                   │                      │      │
│     │ ────────────────────────────────────────>                      │      │
│     │                                         │                      │      │
│     │  2. Response: HTML + Public Key         │                      │      │
│     │     + CSRF Token + JSESSIONID           │                      │      │
│     │ <────────────────────────────────────────                      │      │
│     │                                         │                      │      │
│     │  3. Client-side:                        │                      │      │
│     │     - Generate Session Key (AES)        │                      │      │
│     │     - Encrypt Password (AES)            │                      │      │
│     │     - Encrypt Session Key (RSA)         │                      │      │
│     │                                         │                      │      │
│     │  4. POST /sso/auth (Encrypted Data)     │                      │      │
│     │ ────────────────────────────────────────>                      │      │
│     │                                         │                      │      │
│     │  5. 302 Redirect to LMS                 │                      │      │
│     │ <────────────────────────────────────────                      │      │
│     │                                         │                      │      │
│     │  6. GET /ilos/sso/sso_response.jsp?code=xxx                    │      │
│     │ ─────────────────────────────────────────────────────────────────>    │
│     │                                                                │      │
│     │  7. 로그인 완료 (LMS 세션 생성)                                   │      │
│     │ <─────────────────────────────────────────────────────────────────    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 1단계: 로그인 페이지 접속 (GET)

### 3.1 Client → Server 요청

#### Request URL
```
GET https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp
```

#### Query Parameters
| 파라미터 | 값 | 설명 |
|----------|-----|------|
| `response_type` | `code` | OAuth2 Authorization Code 방식 |
| `client_id` | `lms` | 요청하는 서비스 식별자 |
| `state` | `Random String` | CSRF 방지용 상태 값 |
| `redirect_uri` | `https://lms.mju.ac.kr/ilos/sso/sso_response.jsp` | 인증 후 리다이렉트 URL |

#### Request Headers
```http
GET /sso/auth?... HTTP/1.1
Host: sso.mju.ac.kr
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
```

---

### 3.2 Server → Client 응답

#### Response Headers
```http
HTTP/1.1 200 OK
Content-Type: text/html;charset=UTF-8
Set-Cookie: JSESSIONID=6AF45DE39AAA42BB85D762A01EEEDD6C; Path=/; HttpOnly
Set-Cookie: bandisncdevid=...; Path=/; HttpOnly
Cache-Control: no-cache, no-store, must-revalidate
```

#### 중요 Set-Cookie 항목
| 쿠키 이름 | 용도 |
|-----------|------|
| `JSESSIONID` | 세션 식별자 (Tomcat) |
| `bandisncdevid` | 기기 식별자 (보안 솔루션) |

#### Response Body (HTML) - 핵심 요소

##### Public Key (RSA 공개키)
```html
<input type="hidden" value="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAiLpIB1g9KmkaslpEvZ89iClfGpznC+IavVT7a0/H1LrLBZRpMWCwWW2YLj+gsPKnQvq3ZYYCn6AJ3mjz6/Y2JtvYbEt4rn1eT5nqMA58KTEgxjOaK4nrVNQ7OPYS4dlOaVJOu77JLizcOzRD61aiPgkqvJANsSV2tWJ82afLeX/6vmiuUd5wczB9XFhhgyfYAmExAQMmubgjmoIPXrF0wYpxbQYrXjzGBuSkv9jbs1kHLPWEXVtxE7IbJtLRoBDqbNyELzL8u43gBL3ncjY5P0hV9SeLvbJAcZTRGPHYHePiaayplHiLn9HdoBHYE3rxa6D+n1QESEhVCTFbGVrdEQIDAQAB" id="public-key">
```

##### CSRF Token
```html
<input type="hidden" name="c_r_t" value="j7VO77Aehm8aP0Bqh1M8jNvmZn2osVAykPZMkBGXggY" id="c_r_t">
```

##### Form Action URL
```html
<form id="signin-form" action="https://sso.mju.ac.kr/sso/auth;jsessionid=6AF45DE39AAA42BB85D762A01EEEDD6C?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp&cm_cg_id=6AF45DE39AAA42BB85D762A01EEEDD6C" method="POST">
```

##### Input Fields
```html
<input type="text" id="input-userId" name="user_id" placeholder="아이디">
<input type="password" id="input-password" name="pw" placeholder="비밀번호">
<input type="hidden" name="user_id_enc" id="input-userId-enc">
<input type="hidden" name="pw_enc" id="input-password-enc">
<input type="hidden" name="encsymka" id="input-encsymka">
```

---

## 4. 2단계: 로그인 요청 (POST)

### 4.1 Client-side 암호화 처리 (sign.form.js)

로그인 버튼 클릭 시 JavaScript에서 다음 과정 수행:

```javascript
// 1. Public Key 로드
var publicKeyStr = $('#public-key').val();
bandiJS.setPublicKey(publicKeyStr);

// 2. 세션키 생성 (32 bytes)
var curTime = new Date().getTime();
var keyInfo = bandiJS.genKey(32);

// 3. 세션키를 RSA로 암호화 (키 교환용)
var encKey = bandiJS.encryptJavaPKI(keyInfo.keyStr + ',' + curTime);
$("#input-encsymka").val(encKey);

// 4. 비밀번호를 AES로 암호화
var encPw = bandiJS.encryptBase64AES(pw.trim(), keyInfo);
$("#input-password-enc").val(encPw);
$("#input-password").val('');  // 평문 비밀번호 삭제

// 5. 키 정보 메모리에서 삭제
bandiJS.deleteKey(keyInfo);
```

### 4.2 Client → Server 요청

#### Request URL
```
POST https://sso.mju.ac.kr/sso/auth;jsessionid=XXX?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp&cm_cg_id=XXX
```

#### Request Headers
```http
POST /sso/auth;jsessionid=XXX?... HTTP/1.1
Host: sso.mju.ac.kr
Content-Type: application/x-www-form-urlencoded
Origin: https://sso.mju.ac.kr
Referer: https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&...
Cookie: JSESSIONID=XXX; bandisncdevid=XXX
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...
```

#### Request Body (Form Data)
| 필드명 | 타입 | 값 예시 | 설명 |
|--------|------|---------|------|
| `user_id` | Plain | `학번` | 사용자 ID (평문) |
| `pw` | Empty | `` | 평문 비밀번호 (JS에서 비움) |
| `pw_enc` | Encrypted | `Base64(AES(...))` | AES로 암호화된 비밀번호 |
| `encsymka` | Encrypted | `Base64(RSA(...))` | RSA로 암호화된 세션키+타임스탬프 |
| `c_r_t` | Token | `j7VO77...` | CSRF 토큰 |
| `user_id_enc` | Empty/Encrypted | `` | 암호화된 사용자 ID (선택) |

#### 실제 전송 데이터 예시
```
user_id=20210000&pw=&pw_enc=d1FGNzJ...&encsymka=YmFzZTY0...&c_r_t=j7VO77...
```

### 4.3 Server 처리 로직 (추정)

1. **CSRF 토큰 검증**: `c_r_t` 값이 세션에 저장된 값과 일치하는지 확인
2. **RSA 복호화**: Private Key로 `encsymka`를 복호화하여 세션키 + 타임스탬프 획득
3. **타임스탬프 검증**: 요청 시간이 유효한 범위 내인지 확인
4. **AES 복호화**: 획득한 세션키로 `pw_enc`를 복호화하여 평문 비밀번호 획득
5. **인증**: 사용자 ID와 비밀번호로 DB 조회 및 검증
6. **Authorization Code 발급**: 인증 성공 시 일회용 코드 생성

### 4.4 Server → Client 응답

#### 성공 시 (302 Redirect)
```http
HTTP/1.1 302 Found
Location: https://lms.mju.ac.kr/ilos/sso/sso_response.jsp?code=AUTHORIZATION_CODE&state=Random%20String
Set-Cookie: (추가 세션 쿠키)
```

#### 실패 시 (200 OK + Error)
```http
HTTP/1.1 200 OK
Content-Type: text/html;charset=UTF-8
```
HTML 내 JavaScript로 에러 메시지 전달:
```javascript
var errorMsg = "아이디 또는 비밀번호가 일치하지 않습니다.";
alert(errorMsg);
```

---

## 5. 3단계: 리다이렉트 처리

### 5.1 Client → LMS 서버

#### Request URL
```
GET https://lms.mju.ac.kr/ilos/sso/sso_response.jsp?code=AUTHORIZATION_CODE&state=Random%20String
```

#### Request Headers
```http
GET /ilos/sso/sso_response.jsp?code=XXX&state=... HTTP/1.1
Host: lms.mju.ac.kr
Cookie: (SSO에서 받은 쿠키들)
```

### 5.2 LMS Server 처리

1. **Authorization Code 검증**: SSO 서버에 코드 유효성 확인
2. **Access Token 교환**: (서버 간 통신)
3. **사용자 정보 조회**: Access Token으로 사용자 정보 요청
4. **LMS 세션 생성**: 자체 세션 생성 및 쿠키 발급

### 5.3 LMS → Client 응답

```http
HTTP/1.1 302 Found
Location: https://lms.mju.ac.kr/ilos/main/main_form.acl
Set-Cookie: LMS_SESSION=xxx; Path=/; HttpOnly
```

---

## 6. 암호화 상세

### 6.1 암호화 방식 개요

```
┌──────────────────────────────────────────────────────────────────┐
│                    하이브리드 암호화 방식                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [비밀번호]                                                        │
│      │                                                           │
│      ▼                                                           │
│  ┌─────────────────┐                                             │
│  │  AES-256-CBC    │◄───── [세션키 (32 bytes)]                   │
│  │  암호화         │              │                              │
│  └────────┬────────┘              │                              │
│           │                       ▼                              │
│           │               ┌───────────────┐                      │
│           │               │ RSA-PKCS1-v1.5│◄─── [공개키]          │
│           │               │    암호화      │                      │
│           │               └───────┬───────┘                      │
│           │                       │                              │
│           ▼                       ▼                              │
│      [pw_enc]               [encsymka]                           │
│           │                       │                              │
│           └───────────┬───────────┘                              │
│                       │                                          │
│                       ▼                                          │
│               [ POST Request ]                                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 RSA 암호화 (키 교환용)

| 항목 | 값 |
|------|-----|
| 알고리즘 | RSA |
| 패딩 | PKCS1-v1.5 |
| 키 길이 | 2048 bits |
| 암호화 대상 | `세션키,타임스탬프` (예: `ABCdef123...,1700000000000`) |
| 결과 형식 | Base64 |

#### bandi.lib.common.js 코드
```javascript
encryptJavaPKI: function (value) {
    return crypt.encryptPKI(value, 'RSAES-PKCS1-V1_5');
}
```

### 6.3 AES 암호화 (비밀번호용)

| 항목 | 값 |
|------|-----|
| 알고리즘 | AES-256-CBC |
| 키 길이 | 32 bytes (256 bits) |
| IV | 키에서 파생 (마지막 16 bytes) |
| 패딩 | PKCS7 |
| 결과 형식 | Base64 |

#### 세션키 생성 (genKey)
```javascript
genKey: function(length) {
    // 1. 64 bytes 랜덤 생성 후 Base64 인코딩
    var keyStr = forge.util.encode64(forge.random.getBytesSync(64));
    
    // 2. Salt = 마지막 16자리
    var salt = keyStr.substring(keyStr.length - 16);
    
    // 3. PBKDF2로 키 도출
    var keyBytes = forge.pkcs5.pbkdf2(keyStr, salt, 1024, length);
    
    // 4. IV = 키의 마지막 16 bytes
    var ivBytes = keyBytes.slice(keyBytes.length - 16);
    
    return {
        length: length,
        key: keyBytes,
        iv: ivBytes,
        keyStr: keyStr  // 이 값이 RSA로 암호화됨
    };
}
```

#### AES 암호화 (encryptBase64AES)
```javascript
encryptBase64AES: function(value, keyInfo, isEncodeUri, isUtf8) {
    var encValue = value;
    
    // 한글 처리
    if (!isAscii(value)) {
        encValue = encodeURIComponent('__h_' + value);
    } else if (isEncodeUri) {
        encValue = encodeURIComponent(value);
    }
    
    // Base64 인코딩
    var enc64Value = isUtf8 
        ? forge.util.encodeUtf8(encValue) 
        : forge.util.encode64(encValue);
    
    // AES-CBC 암호화
    var cipher = forge.cipher.createCipher('AES-CBC', keyInfo.key);
    cipher.start({iv: keyInfo.iv});
    cipher.update(forge.util.createBuffer(enc64Value));
    cipher.finish();
    
    return forge.util.encode64(cipher.output.bytes());
}
```

### 6.4 Python 구현 예시

```python
import base64
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Util.Padding import pad

def get_random_string(length=32):
    """32자리 랜덤 세션키 생성"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def encrypt_session_key(session_key, timestamp, public_key_str):
    """RSA로 세션키+타임스탬프 암호화"""
    pem_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
    rsa_key = RSA.import_key(pem_key)
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    
    payload = f"{session_key},{timestamp}".encode('utf-8')
    encrypted = cipher_rsa.encrypt(payload)
    
    return base64.b64encode(encrypted).decode('utf-8')

def encrypt_password(password, session_key):
    """AES-256-CBC로 비밀번호 암호화"""
    key_bytes = session_key.encode('utf-8')
    iv = key_bytes[:16]  # IV = 키의 앞 16 bytes
    
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    padded = pad(password.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded)
    
    return base64.b64encode(encrypted).decode('utf-8')
```

---

## 7. 쿠키 및 세션 관리

### 7.1 쿠키 종류

| 쿠키 이름 | 발급 서버 | 용도 | 수명 |
|-----------|-----------|------|------|
| `JSESSIONID` | SSO | Java 세션 식별 | Session |
| `bandisncdevid` | SSO | 기기 식별 (보안) | Persistent |
| `bdsso_lang` | SSO | 언어 설정 | Persistent |
| `__remb_me_` | SSO | 아이디 저장 여부 | 1일 |
| `__remb_me_id_` | SSO | 저장된 아이디 | 1일 |

### 7.2 remember.me.js 동작

```javascript
// 로그인 폼 제출 시
$('#signin-form').submit(function() {
    if ($('#remember-me').is(':checked')) {
        // 쿠키에 아이디 저장 (1일)
        $.cookie('__remb_me_id_', $('#input-userId').val(), { expires: 1, path: '/' });
        $.cookie('__remb_me_', true, { expires: 1, path: '/' });
    } else {
        // 쿠키 삭제
        $.removeCookie('__remb_me_id_', { path: '/' });
        $.removeCookie('__remb_me_', { path: '/' });
    }
});
```

### 7.3 세션 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│                        세션/쿠키 흐름                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [1] GET /sso/auth                                              │
│      ────────────────────────────────────────>                  │
│      <──────────────────────────────────────── Set-Cookie:      │
│                                                 JSESSIONID=A    │
│                                                 bandisncdevid=X │
│                                                                 │
│  [2] POST /sso/auth (Cookie: JSESSIONID=A)                      │
│      ────────────────────────────────────────>                  │
│      <──────────────────────────────────────── 302 + Set-Cookie │
│                                                 (세션 갱신)       │
│                                                                 │
│  [3] GET /ilos/sso/sso_response.jsp                             │
│      ────────────────────────────────────────>                  │
│      <──────────────────────────────────────── Set-Cookie:      │
│                                                 LMS_SESSION=B   │
│                                                                 │
│  [4] GET /ilos/main/main_form.acl                               │
│      (Cookie: LMS_SESSION=B)                                    │
│      ────────────────────────────────────────>                  │
│      <──────────────────────────────────────── 200 OK           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. 에러 처리

### 8.1 일반적인 에러 메시지

| 에러 메시지 | 원인 |
|-------------|------|
| `아이디 또는 비밀번호가 일치하지 않습니다.` | 인증 실패 |
| `세션이 만료되었습니다.` | JSESSIONID 무효 |
| `CSRF 토큰이 유효하지 않습니다.` | c_r_t 불일치 |
| `암호화 오류` | AES/RSA 복호화 실패 |

### 8.2 에러 응답 형식

```javascript
// index.js - 에러 처리
window.onload = function() {
    var errorMsg = null;
    if (errorMsg) {
        alert(errorMsg);
        location.href = '/sso/auth?cm_cg_id=' + null;
    }
}
```

### 8.3 2차 인증 (교직원)

교직원의 경우 추가적인 2차 인증이 필요할 수 있습니다:

```javascript
// twofact.form.js
$('#two-factor-form').submit(function(event) {
    var tfVal = $('#input-tf_val').val();  // OTP 또는 인증 코드
    
    // 암호화 후 전송
    var encTfVal = bandiJS.encryptBase64AES(tfVal.trim(), keyInfo, true);
    $("#input-tf_val-enc").val(encTfVal);
});
```

---

## 부록: 요청/응답 요약표

### A. GET 요청 (로그인 페이지)

| 구분 | 항목 | 값 |
|------|------|-----|
| **Request** | Method | `GET` |
| | URL | `/sso/auth?response_type=code&client_id=lms&...` |
| | Headers | `User-Agent`, `Accept`, `Accept-Language` |
| **Response** | Status | `200 OK` |
| | Headers | `Set-Cookie: JSESSIONID`, `Set-Cookie: bandisncdevid` |
| | Body | HTML (public-key, c_r_t, form 포함) |

### B. POST 요청 (로그인)

| 구분 | 항목 | 값 |
|------|------|-----|
| **Request** | Method | `POST` |
| | URL | `/sso/auth;jsessionid=XXX?response_type=code&...` |
| | Headers | `Content-Type: application/x-www-form-urlencoded` |
| | | `Cookie: JSESSIONID=XXX` |
| | | `Origin: https://sso.mju.ac.kr` |
| | | `Referer: https://sso.mju.ac.kr/sso/auth?...` |
| | Body | `user_id`, `pw_enc`, `encsymka`, `c_r_t` |
| **Response (성공)** | Status | `302 Found` |
| | Headers | `Location: https://lms.mju.ac.kr/ilos/sso/sso_response.jsp?code=XXX` |
| **Response (실패)** | Status | `200 OK` |
| | Body | HTML with JavaScript `alert(errorMsg)` |

---

## 참고 자료

- `/명지대학교 통합로그인_files/sign.form.js.다운로드` - 로그인 폼 처리
- `/명지대학교 통합로그인_files/bandi.lib.common.js.다운로드` - 암호화 라이브러리
- `/명지대학교 통합로그인_files/forge.min.js.다운로드` - Forge 암호화 라이브러리
- `/mju_loginv4.py`, `/mju_loginv5.py` - Python 구현 예시
