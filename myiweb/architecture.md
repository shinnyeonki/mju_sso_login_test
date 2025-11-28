# `myiweb` 모듈 아키텍처 및 사용법 문서

## 1. 개요

`myiweb` 모듈은 명지대학교의 통합정보시스템(MyiWeb, MSI) 및 SSO(Single Sign-On) 시스템과 상호작용하여 학생 정보를 조회하는 Python 라이브러리입니다. 이 문서는 `myiweb` 모듈의 아키텍처, 주요 컴포넌트, 그리고 사용자가 라이브러리를 효과적으로 활용할 수 있는 방법에 대해 설명합니다.

`myiweb`은 복잡한 SSO 로그인 절차(RSA/AES 하이브리드 암호화, CSRF 토큰 관리, 다단계 리다이렉션)를 자동화하며, 로그인 후 학생카드 정보나 학적변동내역과 같은 특정 정보를 추출합니다.

## 2. 모듈 구조

```
myiweb/
├── __init__.py           # 패키지 초기화 및 공개 API 정의
├── abc.py                # 추상 기본 클래스 (BaseFetcher) 정의
├── client.py             # SSO 로그인 관리 및 서비스 팩토리 (Client)
├── crypto.py             # SSO 로그인에 사용되는 RSA/AES 암호화 유틸리티
├── exceptions.py         # 커스텀 예외 클래스
├── sso.py                # SSO 통합 로그인 자동화 클래스 (MJUSSOLogin)
├── student_card.py       # 학생카드 정보 (StudentCard) 및 조회 서비스 (StudentCardService)
├── student_changelog.py  # 학적변동내역 정보 (StudentChangeLog) 및 조회 서비스 (StudentChangeLogService)
├── utils.py              # 로깅, 색상 코드 등 공통 유틸리티
├── __main__.py           # `python -m myiweb` 실행을 위한 CLI 엔트리포인트
├── examples.py           # 사용 예제 코드
└── architecture.md       # 본 아키텍처 문서
```

## 3. 최상위 API (High-Level API) 및 사용법

사용자의 편의를 위해, 각 정보의 데이터 클래스에 고수준의 `fetch` 클래스 메서드를 제공합니다. 이 메서드는 내부적으로 SSO 로그인부터 정보 조회까지의 모든 과정을 캡슐화합니다.

```python
from myiweb import StudentCard, StudentChangeLog, MyIWebError
import os
from dotenv import load_dotenv

load_dotenv()
user_id = os.getenv('MJU_ID')
user_pw = os.getenv('MJU_PW')

try:
    # 학생카드 정보 조회
    student_card = StudentCard.fetch(user_id, user_pw)
    print("학생카드 정보:")
    print(student_card.to_dict())

    # 학적변동내역 조회
    change_log = StudentChangeLog.fetch(user_id, user_pw)
    print("\n학적변동내역:")
    print(change_log.to_dict())

except MyIWebError as e:
    print(f"오류 발생: {e}")
```

**주의**: 각 `fetch()` 호출은 내부적으로 독립적인 SSO 로그인 과정을 수행합니다. 따라서 여러 종류의 정보를 조회할 경우, 로그인 과정이 반복될 수 있습니다.

## 4. 핵심 컴포넌트 설명

### 4.1. `myiweb.Client`

*   **역할**: SSO 로그인 과정을 관리하고, 로그인된 `requests.Session` 객체를 유지합니다. 또한, 특정 정보를 조회하기 위한 '서비스' 객체(예: `StudentCardService`, `StudentChangeLogService`)를 생성하는 팩토리(Factory) 역할을 합니다.
*   **내부 동작**: `Client` 객체가 생성될 때 `myiweb.sso.MJUSSOLogin`을 사용하여 SSO 로그인을 수행하고, 성공적인 세션을 확보합니다.
*   **고수준 API와의 관계**: `StudentCard.fetch()`와 같은 고수준 API는 내부적으로 `Client`를 생성하여 사용합니다.

### 4.2. `myiweb.abc.BaseFetcher`

*   **역할**: `StudentCardService`와 `StudentChangeLogService` 같은 모든 '서비스' 클래스가 상속받는 추상 기본 클래스(Abstract Base Class)입니다.
*   **주요 기능**:
    *   `requests.Session`, 사용자 비밀번호(`user_pw`), 상세 로깅 여부(`verbose`)를 공통으로 관리합니다.
    *   `fetch()`라는 추상 메서드를 정의하여, 모든 하위 서비스 클래스가 반드시 이 메서드를 구현하도록 강제합니다.
    *   MSI 페이지에서 CSRF 토큰을 추출하는 `_get_csrf_token()`과 `_extract_csrf_from_html()` 같은 **공통 유틸리티 메서드**를 제공하여 코드 중복을 방지합니다.

### 4.3. `myiweb.sso.MJUSSOLogin`

*   **역할**: 명지대학교 SSO 시스템에 로그인하는 복잡한 절차를 자동화합니다.
*   **주요 동작**:
    *   SSO 로그인 페이지에서 RSA 공개키, CSRF 토큰, 폼 액션 URL 등을 파싱합니다.
    *   `myiweb.crypto` 모듈을 사용하여 아이디와 비밀번호를 하이브리드 암호화(RSA+AES)합니다.
    *   암호화된 자격 증명을 SSO 서버에 제출하고, 여러 단계의 HTTP 리다이렉션 및 JavaScript 폼 자동 제출을 처리하여 최종적으로 인증된 `requests.Session` 객체를 획득합니다.
*   **사용처**: 주로 `myiweb.Client` 클래스 내부에서 사용됩니다.

### 4.4. `myiweb.crypto`

*   **역할**: SSO 로그인 과정에서 필요한 암호화(RSA/AES 하이브리드 암호화)를 수행합니다.
*   **주요 기능**:
    *   대칭키(세션키) 생성 및 PBKDF2 키 파생.
    *   RSA-PKCS1-v1.5를 이용한 세션키 암호화.
    *   AES-256-CBC를 이용한 비밀번호 암호화.

### 4.5. `myiweb.student_card.StudentCard` & `StudentCardService`

*   **`StudentCard` (데이터 클래스)**: 학생카드의 상세 정보(학번, 이름, 학적상태, 주소, 사진 Base64 등)를 담는 데이터 구조입니다. `to_dict()` 및 `print_summary()` 메서드를 통해 정보를 정제된 형태로 제공합니다.
*   **`StudentCardService` (조회 서비스)**: `BaseFetcher`를 상속받으며, SSO 로그인된 세션을 사용하여 학생카드 정보를 조회하는 구체적인 로직을 구현합니다.
    *   **특징**: 학생카드 정보는 보안을 위해 **2차 비밀번호 인증**을 요구하므로, `fetch()` 메서드 내부에 이 과정을 처리하는 로직(비밀번호 재제출, 리다이렉션 폼 처리)이 포함되어 있습니다.
    *   `_parse_info()` 메서드가 응답 HTML에서 학생카드 정보를 추출합니다.

### 4.6. `myiweb.student_changelog.StudentChangeLog` & `StudentChangeLogService`

*   **`StudentChangeLog` (데이터 클래스)**: 학생의 학적변동내역 정보(학번, 이름, 학적상태, 학년, 이수학기, 학부(과) 등)를 담는 데이터 구조입니다. `to_dict()` 및 `print_summary()` 메서드를 통해 정보를 제공합니다.
*   **`StudentChangeLogService` (조회 서비스)**: `BaseFetcher`를 상속받으며, SSO 로그인된 세션을 사용하여 학적변동내역을 조회하는 구체적인 로직을 구현합니다.
    *   **특징**: 학생카드 조회와 달리, **2차 비밀번호 인증 과정이 필요 없습니다.** 따라서 `fetch()` 메서드의 내부 로직이 `StudentCardService`보다 간결합니다.
    *   `_parse_info()` 메서드가 응답 HTML에서 학적변동내역 정보를 추출합니다.

### 4.7. `myiweb.exceptions`

*   **역할**: `myiweb` 모듈에서 발생할 수 있는 다양한 오류 상황(네트워크 오류, 페이지 파싱 오류, 잘못된 자격 증명 등)을 나타내는 커스텀 예외 클래스들을 정의합니다. 일관된 오류 처리를 가능하게 합니다.

### 4.8. `myiweb.utils`

*   **역할**: 콘솔 로깅(색상 코드 포함), HTTP 요청/응답 로깅, 민감 정보 마스킹 등 모듈 전반에 걸쳐 사용되는 공통 유틸리티 함수들을 제공합니다.

## 5. 데이터 흐름 예시: `StudentCard.fetch(user_id, user_pw)`

사용자가 `StudentCard.fetch(user_id, user_pw)`를 호출할 때 내부적으로 발생하는 주요 호출 흐름은 다음과 같습니다.

1.  **`StudentCard.fetch(user_id, user_pw, ...)` 호출**:
    *   내부적으로 `client = Client(user_id, user_pw, verbose=...)`를 생성합니다.
2.  **`Client.__init__(user_id, user_pw, ...)`**:
    *   `sso_login_manager = MJUSSOLogin(user_id, user_pw, ...)`를 생성합니다.
    *   `session = sso_login_manager.login(service='msi')`를 호출하여 SSO 로그인 절차를 시작합니다.
3.  **`MJUSSOLogin.login(...)`**:
    *   SSO 로그인 페이지에 `GET` 요청을 보내 HTML을 받아옵니다.
    *   HTML에서 RSA 공개키, CSRF 토큰, 폼 액션 URL을 파싱합니다.
    *   `myiweb.crypto` 모듈을 사용하여 비밀번호를 암호화하고, 세션키 정보를 RSA로 암호화합니다.
    *   암호화된 자격 증명을 SSO 서버에 `POST` 요청으로 전송합니다.
    *   여러 단계의 HTTP 리다이렉션 및 JavaScript 폼 제출을 처리하여 `msi.mju.ac.kr` 도메인에 대한 유효한 `requests.Session`을 얻습니다.
    *   획득한 `session` 객체를 `Client`에게 반환합니다.
4.  **`StudentCard.fetch(...)` (계속)**:
    *   `card_service = client.student_card()`를 호출하여 `StudentCardService(session, user_pw, ...)` 인스턴스를 얻습니다.
    *   `student_card_object = card_service.fetch()`를 호출하여 학생카드 정보 조회를 시작합니다.
5.  **`StudentCardService.fetch()`**:
    *   `super()._get_csrf_token()` (즉, `BaseFetcher._get_csrf_token()`)을 호출하여 MSI 페이지에서 CSRF 토큰을 획득합니다.
    *   `_access_student_card_page()` 메서드를 통해 `pgmid='W_SUD005'`를 포함한 `POST` 요청으로 학생카드 페이지에 접근합니다.
    *   응답 HTML을 분석하여 **2차 비밀번호 입력 폼이 필요한지 확인합니다.**
    *   **2차 비밀번호가 필요한 경우**:
        *   사용자 비밀번호(`user_pw`)를 포함하여 `_submit_password()` 메서드를 통해 2차 인증 `POST` 요청을 보냅니다.
        *   `_handle_redirect_form()` 메서드로 2차 인증 성공 후의 리다이렉션 폼을 처리합니다.
    *   최종 응답 HTML을 `_parse_info()` 메서드로 파싱하여 `StudentCard` 데이터 객체를 생성하고 반환합니다.
6.  **`StudentCard.fetch(...)` (종료)**:
    *   `StudentCard` 데이터 객체를 사용자에게 반환합니다.

## 6. 확장성: 새로운 정보 조회 기능 추가

`myiweb` 모듈에 새로운 정보(예: 성적 조회, 수강신청 내역)를 추가하려면 다음 단계를 따릅니다.

1.  **새 데이터 클래스 정의**: 조회할 정보를 담을 새로운 `dataclass`를 `myiweb/new_data.py`와 같이 정의합니다 (예: `Grade`, `CourseRegistration`). 이 클래스에는 `to_dict()`와 `print_summary()` 메서드를 구현하여 일관성을 유지합니다.
2.  **새 서비스 클래스 정의**: `BaseFetcher`를 상속받는 `NewDataService` 클래스를 `myiweb/new_data.py`에 함께 정의합니다 (예: `GradeService`, `CourseRegistrationService`).
    *   `fetch()` 메서드를 구현하여, 해당 정보를 조회하는 구체적인 HTTP 요청 및 파싱 로직을 포함합니다.
    *   필요에 따라 2차 비밀번호 인증 여부 등 해당 정보 조회만의 특수 로직을 구현합니다.
    *   `_parse_info()` 메서드를 구현하여 HTML 응답을 새로 정의한 데이터 클래스로 파싱합니다.
3.  **Client 확장**: `myiweb/client.py`의 `Client` 클래스에 `new_data(self) -> NewDataService`와 같은 새로운 메서드를 추가하여 새 서비스 객체를 반환하도록 합니다.
4.  **최상위 API 추가 (선택 사항)**: 새로운 데이터 클래스(예: `Grade`)에 `fetch(cls, user_id, user_pw, verbose=True)` 클래스 메서드를 추가하여 사용자 편의성을 높입니다. 이 메서드는 `Client`와 `NewDataService`를 내부적으로 사용합니다.
5.  **`__init__.py` 업데이트**: `myiweb/__init__.py` 파일에 새로 추가된 데이터 클래스를 `__all__` 리스트에 추가하여 외부에서 임포트할 수 있도록 합니다.
6.  **문서 및 예제 업데이트**: `README.md`, `examples.py`, `architecture.md`를 업데이트하여 새로운 기능을 설명하고 사용법을 제시합니다.
