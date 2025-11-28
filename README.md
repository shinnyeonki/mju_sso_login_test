# MJU Univ Auth

명지대학교 학생 인증 및 정보 조회를 위한 Python 라이브러리 및 REST API 서버입니다.

## 📋 목차

- [1. Python 라이브러리](#1-python-라이브러리-pypi)
  - [설치](#설치)
  - [사용법](#사용법)
  - [StudentInfo 클래스](#studentinfo-클래스)
  - [예외 처리](#예외-처리)
- [2. REST API 서버](#2-rest-api-서버)
  - [아키텍처 개요](#아키텍처-개요)
  - [API 명세](#api-명세)
  - [서버 배포 가이드](#서버-배포-가이드)

---

## 1. Python 라이브러리 (PyPI)

외부 개발자가 pip로 쉽게 설치하고 사용할 수 있는 Python 라이브러리입니다.

### 설치

```bash
pip install mju_univ_auth
```

### 사용법

```python
import os
from mju_univ_auth import StudentInfo
from mju_univ_auth.exceptions import InvalidCredentialsError, NetworkError

# ID와 비밀번호는 환경 변수 등 안전한 곳에서 가져오는 것을 권장합니다.
mju_id = os.getenv("MJU_ID", "60221234")
mju_pw = os.getenv("MJU_PW", "your_password")

try:
    # StudentInfo 클래스 메서드를 직접 호출하여 로그인 및 정보 조회
    student_info = StudentInfo.from_login(user_id=mju_id, user_pw=mju_pw)

    # 반환된 객체에서 직접 데이터에 접근
    print(f"로그인 성공: {student_info.name_korean} ({student_info.student_id})")
    print(f"소속: {student_info.department}")
    print(f"상태: {student_info.status}")

    # 학생 사진(이미지) 처리 - Base64 디코딩
    if student_info.photo_base64:
        import base64
        image_data = base64.b64decode(student_info.photo_base64)
        with open(f"{student_info.student_id}.jpg", "wb") as f:
            f.write(image_data)
        print(f"'{student_info.student_id}.jpg' 이름으로 학생 사진 저장 완료!")

except InvalidCredentialsError as e:
    print(f"로그인 실패: 아이디 또는 비밀번호를 확인해주세요. ({e})")
except NetworkError as e:
    print(f"네트워크 오류: 학교 서버에 접속할 수 없습니다. ({e})")
except Exception as e:
    print(f"알 수 없는 오류 발생: {e}")
```

### StudentInfo 클래스

`StudentInfo`는 명지대학교 학생 정보 시스템에서 조회 가능한 모든 학생 정보를 담는 데이터 클래스입니다.

#### 필드 목록

| 필드명 | 타입 | 설명 | 예시 값 |
|--------|------|------|---------|
| `student_id` | `str` | 학번 | `"60222100"` |
| `name_korean` | `str` | 한글 성명 | `"홍길동"` |
| `name_english_first` | `str` | 영문 성 (Last Name) | `"Hong"` |
| `name_english_last` | `str` | 영문 이름 (First Name) | `"Gil Dong"` |
| `grade` | `str` | 학년 | `"4"` |
| `status` | `str` | 학적 상태 | `"재학"` |
| `department` | `str` | 학부(과)명 | `"(반도체·ICT대학) 컴퓨터공학전공"` |
| `advisor` | `str` | 상담 교수 | `"홍교수 (컴퓨터공학전공)"` |
| `design_advisor` | `str` | 학생설계전공지도교수 | `" ()"` |
| `phone` | `str` | 전화번호 | `"010-1234-5678"` |
| `mobile` | `str` | 휴대폰 번호 | `"01012345678"` |
| `email` | `str` | 이메일 주소 | `"example@mju.ac.kr"` |
| `current_zip` | `str` | 현 거주지 우편번호 | `"12345"` |
| `current_address1` | `str` | 현 거주지 주소 1 | `"경기도 용인시 처인구"` |
| `current_address2` | `str` | 현 거주지 주소 2 | `"명지로 116"` |
| `registered_zip` | `str` | 주민등록 주소 우편번호 | `"12345"` |
| `registered_address1` | `str` | 주민등록 주소 1 | `"경기도 용인시 처인구"` |
| `registered_address2` | `str` | 주민등록 주소 2 | `"명지로 116"` |
| `photo_base64` | `str` | 학생 사진 (JPEG, Base64 인코딩) | `/9j/4AAQSkZJRg...` |
| `focus_newsletter` | `bool` | 명지포커스 책자 수신 동의 여부 | `True` / `False` |
| `raw_data` | `Dict[str, Any]` | 파싱된 원본 데이터 | `{'학번': '60222100', ...}` |

#### 유틸리티 메서드

- **`to_dict() -> Dict[str, Any]`**: StudentInfo 객체를 JSON 직렬화가 용이한 딕셔너리로 반환
- **`print_summary() -> None`**: 콘솔에 학생 정보 요약을 출력 (디버깅용)

### 예외 처리

| 예외 클래스 | 설명 |
|-------------|------|
| `InvalidCredentialsError` | 아이디 또는 비밀번호가 틀린 경우 |
| `NetworkError` | 학교 서버에 접속할 수 없는 경우 |
| `SessionExpiredError` | 로그인 세션이 만료된 경우 |
| `PageParsingError` | 학생 정보 페이지 파싱 실패 (학교 시스템 변경 가능성) |
| `MyIWebError` | 기타 라이브러리 내부 오류 |

---

## 2. REST API 서버

다른 프로그래밍 언어에서도 HTTP 요청을 통해 쉽게 사용할 수 있는 REST API 서버입니다.

### 아키텍처 개요

```
사용자 요청 (HTTPS)
        │
        ▼
┌───────────────────────────────────────────┐
│  Apache (Reverse Proxy + SSL)             │
│  mju-univ-auth.shinnk.kro.kr:443          │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│  Docker Container (FastAPI)               │
│  127.0.0.1:8000                           │
└───────────────────────────────────────────┘
```

1. **사용자 요청:** `https://mju-univ-auth.shinnk.kro.kr` 로 접속
2. **Apache:** 443 포트에서 SSL 복호화 후 내부 8000번 포트로 전달
3. **Docker:** FastAPI 앱이 요청을 처리하고 응답 반환

### API 명세

#### 엔드포인트

```
POST /api/v1/student-card
```

#### Request Body

```json
{
  "user_id": "YOUR_STUDENT_ID",
  "password": "YOUR_PASSWORD"
}
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "student_id": "60221234",
    "name_korean": "홍길동",
    "name_english": "GIL DONG HONG",
    "grade": "4",
    "status": "재학",
    "department": "(반도체·ICT대학) 컴퓨터정보통신공학부 컴퓨터공학전공",
    "advisor": "홍교수 (컴퓨터정보통신공학부 컴퓨터공학전공)",
    "phone": "010-1234-5678",
    "mobile": "01012345678",
    "email": "example@mju.ac.kr",
    "current_address": {
      "zip": "12345",
      "address1": "경기도 용인시 처인구 명지로 116",
      "address2": "학생회관"
    },
    "registered_address": {
      "zip": "12345",
      "address1": "경기도 용인시 처인구 명지로 116",
      "address2": "학생회관"
    },
    "photo_base64": "/9j/4AAQSkZJRgABAg...",
    "focus_newsletter": false
  }
}
```

#### Error Responses

| 상태 코드 | 상황 | 응답 예시 |
|-----------|------|-----------|
| `400 Bad Request` | 필수 필드 누락 | `{"detail": "요청 본문 형식이 올바르지 않거나 필수 필드가 누락되었습니다."}` |
| `401 Unauthorized` | 인증 실패 | `{"detail": "아이디 또는 비밀번호가 틀렸습니다."}` |
| `500 Internal Server Error` | 서버 내부 오류 | `{"detail": "내부 서버 오류가 발생했습니다."}` |
| `502 Bad Gateway` | 학교 서버 접속 불가 | `{"detail": "학교 서버에 연결할 수 없습니다."}` |

#### 사용 예시

**cURL:**
```bash
curl -X POST https://mju-univ-auth.shinnk.kro.kr/api/v1/student-card \
     -H "Content-Type: application/json" \
     -d '{"user_id": "60221234", "password": "your_password"}'
```

**JavaScript (fetch):**
```javascript
const response = await fetch('https://mju-univ-auth.shinnk.kro.kr/api/v1/student-card', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: '60221234', password: 'your_password' })
});
const data = await response.json();
console.log(data);
```

---

### 서버 배포 가이드

Docker(FastAPI) + Apache(Reverse Proxy & SSL) 조합으로 서버를 배포하는 전체 가이드입니다.

#### Step 1: 프로젝트 디렉토리 구성

```bash
mkdir -p ~/mju-auth-project
cd ~/mju-auth-project
```

#### Step 2: requirements.txt 작성

```text
fastapi
uvicorn
requests
beautifulsoup4
lxml
pydantic
```

#### Step 3: main.py 작성

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from mju_univ_auth import StudentInfo
from mju_univ_auth.exceptions import InvalidCredentialsError, NetworkError

app = FastAPI(
    title="MJU Student Auth API",
    description="명지대학교 학생 인증 및 정보 조회 API",
    version="1.0.0"
)

class StudentAuthRequest(BaseModel):
    user_id: str
    password: str

@app.post("/api/v1/student-card")
async def get_student_card(req: StudentAuthRequest):
    try:
        student_info = StudentInfo.from_login(req.user_id, req.password)
        return {"success": True, "data": student_info.to_dict()}
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 틀렸습니다."
        )
    except NetworkError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="학교 서버에 접속할 수 없습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 내부 오류가 발생했습니다."
        )
```

#### Step 4: Dockerfile 작성

```dockerfile
# Python 3.9 슬림 버전 사용
FROM python:3.9-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 5: Docker 빌드 및 실행

```bash
# 이미지 빌드
docker build -t mju-auth-server .

# 컨테이너 실행
docker run -d -p 8000:8000 --restart unless-stopped --name mju-api mju-auth-server

# 테스트
curl http://127.0.0.1:8000/docs
```

#### Step 6: Apache 설치 및 리버스 프록시 설정

```bash
# Apache 설치 및 모듈 활성화
sudo apt update
sudo apt install apache2 -y
sudo a2enmod proxy proxy_http ssl headers
sudo systemctl restart apache2
```

**VirtualHost 설정 파일 생성:**

```bash
sudo vim /etc/apache2/sites-available/mju-univ-auth.conf
```

```apache
<VirtualHost *:80>
    ServerName mju-univ-auth.shinnk.kro.kr
    ServerAdmin webmaster@localhost

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    ErrorLog ${APACHE_LOG_DIR}/mju-auth-error.log
    CustomLog ${APACHE_LOG_DIR}/mju-auth-access.log combined
</VirtualHost>
```

```bash
# 사이트 활성화
sudo a2ensite mju-univ-auth.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

#### Step 7: HTTPS (SSL) 설정 (Certbot)

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-apache -y

# 인증서 발급 및 자동 설정
sudo certbot --apache -d mju-univ-auth.shinnk.kro.kr
```

설정 중 Redirect 옵션은 `2`번 (HTTPS 리다이렉트)을 선택합니다.

#### Step 8: 최종 테스트

1. **브라우저:** `https://mju-univ-auth.shinnk.kro.kr/docs` 접속하여 Swagger UI 확인
2. **API 호출:**
   ```bash
   curl -X POST https://mju-univ-auth.shinnk.kro.kr/api/v1/student-card \
        -H "Content-Type: application/json" \
        -d '{"user_id": "YOUR_ID", "password": "YOUR_PW"}'
   ```

#### (참고) 공유기 포트포워딩

홈 서버 환경에서는 공유기에서 포트포워딩이 필요합니다:
- 외부 포트 `80` → 서버 내부 IP `80`
- 외부 포트 `443` → 서버 내부 IP `443`

> Docker 포트(8000)는 Apache가 내부에서 처리하므로 포트포워딩 불필요

---

## 📌 이미지 처리 방식

라이브러리와 API 모두 학생 사진을 **Base64 인코딩된 문자열**로 제공합니다.

**장점:**
- 별도 파일 저장소나 이미지 URL 관리 불필요
- 사용자가 파일 저장, 웹 표시, 메모리 처리 등 유연하게 선택 가능
- API에서 바이너리 데이터를 JSON에 포함하는 표준적인 방법

**웹에서 바로 표시:**
```html
<img src="data:image/jpeg;base64,{photo_base64}" alt="학생 사진">
```

---

## 📄 License

MIT License