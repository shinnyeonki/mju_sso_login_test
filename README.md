프로젝트의 목표는 2가지야 

### 외부 사용자들에게 공유 라이브러리와

외부 사용자들이 pip 를 통해 쉽게 설치하고 사용할 수 있도록 하고 싶어
일단 코드를 고려하지 않고 어떤 식으로 해야 가장 편리하게 사용할 수 있는지
임포드 구문, 함수 사용법 등을 제시해줘

### 내 서버에서 직접 서빙 (이종 언어에서 사용 가능하도록)

내 서버에서 쉽게 배포할 수 있도록 docker 화 해서 내 서버에서 직접 서빙하고 싶어
사용자 입장에서 어떤식으로 요청을 해서 어떤식으로 반환하는 것이 좋은지 설명해줘
정의서를 계획해줘


### 2개 다 고민되는점


이미지의 경우 어떻게 처리하는 것이 좋을까?
base64 로 그대로 처리해서 



아직 코드는 고치지 말고 어떤 방식으로 해야할지 계획을 세워



---

 안녕하세요! myiweb 프로젝트를 공유 라이브러리와 독립적인 API 서버로 발전시키기 위한 목표에 대해
  잘 이해했습니다. 현재 코드를 수정하기 전에, 각 목표에 대한 최적의 사용 시나리오와 구조를 계획하여
  제안해 드리겠습니다.

  1. 외부용 공유 라이브러리 (PyPI 배포)

  외부 개발자가 pip로 쉽게 설치하고 사용할 수 있도록, 패키지의 API를 명확하고 직관적으로 설계하는
  것이 중요합니다. 현재 myiweb의 구조는 이미 fetch_student_info라는 고수준 API를 제공하고 있어 매우
  좋은 출발점입니다.

  제안하는 사용법: 3가지 API 디자인

  라이브러리 API를 설계하는 데에는 여러 좋은 접근 방식이 있습니다. 각각의 장단점을 살펴보고 최종적으로 가장 파이썬스러운 방식을 채택하는 과정을 보여드리겠습니다.

  1. 절차적 함수 방식 (가장 단순)
  가장 기본적인 방식으로, 특정 기능을 수행하는 함수를 직접 노출합니다.
   * `get_student_info(...)`
   * 느낌: "이 아이디/비밀번호로 학생 정보를 가져와 줘."
   * 장점: 이해하기 매우 쉽습니다.
   * 단점: 기능이 많아지면 `get_`, `fetch_`, `update_` 등 수많은 함수가 생겨 API가 복잡해 보일 수 있습니다.

  2. 라이브러리 진입점 방식 (일반적)
  requests 라이브러리가 `requests.get(...)`을 제공하는 것처럼, 패키지 이름 자체가 진입점이 됩니다.
   * `mju_univ_auth.login(...)`
   * 느낌: "mju_univ_auth 라이브러리야, 로그인해 줘."
   * 장점: 어떤 라이브러리의 기능인지 명확히 알 수 있습니다.
   * 단점: `mju_univ_auth.StudentInfo` 와 같이 다른 객체를 참조할 때 패키지 이름을 반복해야 할 수 있습니다.

  3. 클래스 메서드 방식 (Pythonic/모던) - **채택**
  반환될 객체(`StudentInfo`)가 스스로 정보를 가져오도록 책임을 위임하는 방식입니다. 현대적인 라이브러리(예: Pydantic)에서 많이 사용하는 세련된 설계입니다.
   * `StudentInfo.from_login(...)`
   * 느낌: "`StudentInfo` 객체야, 이 로그인 정보로 너 자신을 생성해."
   * 장점:
      * **직관성**: `StudentInfo`를 만들기 위해 `StudentInfo` 클래스를 사용한다는 것이 매우 직관적입니다.
      * **구조성**: 모든 로직이 `StudentInfo`와 연관되어 코드가 깔끔하고 구조적으로 변합니다.
      * **편의성**: `from mju_univ_auth import StudentInfo` 하나만 임포트하면 모든 것을 해결할 수 있습니다.

  **최종 채택안: 클래스 메서드 방식**

  이 프로젝트는 가장 현대적이고 구조적인 **클래스 메서드 방식**을 채택하여 API를 제공합니다.

  패키지 이름을 `mju_univ_auth`라고 가정하겠습니다.

  **설치:**
  ```shell
  pip install mju_univ_auth
  ```

  **핵심 사용법 (Core Usage):**
  ```python
  import os
  from mju_univ_auth import StudentInfo
  from mju_univ_auth.exceptions import InvalidCredentialsError, NetworkError

  # ID와 비밀번호는 환경 변수 등 안전한 곳에서 가져오는 것을 권장합니다.
  mju_id = os.getenv("MJU_ID", "60221234")
  mju_pw = os.getenv("MJU_PW", "your_password")

  try:
      # StudentInfo 클래스 메서드를 직접 호출하여 모든 복잡한 과정을 처리합니다.
      student_info = StudentInfo.from_login(user_id=mju_id, user_pw=mju_pw)

      # 반환된 객체에서 직접 데이터에 접근합니다.
      print(f"로그인 성공: {student_info.name_korean} ({student_info.student_id})")
      print(f"소속: {student_info.department}")
      print(f"상태: {student_info.status}")

      # 학생 사진(이미지) 처리
      if student_info.photo_base64:
          import base64
          # Base64로 인코딩된 이미지 데이터를 디코딩하여 파일로 저장
          image_data = base64.b64decode(student_info.photo_base64)
          with open(f"{student_info.student_id}.jpg", "wb") as f:
              f.write(image_data)
          print(f"'{student_info.student_id}.jpg' 이름으로 학생 사진 저장 완료!")

  except InvalidCredentialsError as e:
      print(f"로그인 실패: 아이디 또는 비밀번호를 확인해주세요. (서버 메시지: {e})")
  except NetworkError as e:
      print(f"네트워크 오류: 학교 서버에 접속할 수 없습니다. ({e})")
  except Exception as e:
      print(f"알 수 없는 오류 발생: {e}")
  ```

  **설계 설명**
   * **객체 지향 API**: `StudentInfo.from_login()` 메서드를 호출하여 `StudentInfo` 객체를 생성합니다. 사용자는 복잡한 인증, 암호화, 세션 관리에 대해 전혀 신경 쓸 필요가 없습니다.
   * **타입 힌트**: `StudentInfo`라는 명확한 데이터 클래스를 반환하여, 개발자가 어떤 필드를 사용할 수 있는지 쉽게 파악하고 자동완성(auto-completion)의 이점을 누릴 수 있습니다.
   * **체계적인 예외 처리**: `InvalidCredentialsError`, `NetworkError` 등 구체적인 예외를 제공하여 사용자가 오류 상황에 맞춰 정교하게 대응할 수 있도록 합니다.
   * **이미지 처리**: 학생 사진은 `photo_base64` 필드를 통해 Base64로 인코딩된 문자열로 제공하는 것이 가장 좋습니다. 라이브러리 사용자가 이미지 데이터를 파일로 저장하든, 메모리에서 바로 처리하든 유연하게 선택할 수 있습니다.

 StudentInfo는 명지대학교 학생 정보 시스템(MSI)에서 조회 가능한 학생의 모든 정보를 담는 데이터 클래스입니다. myiweb/student_card.py에 정의된 내용을 기반으로 상세 필드를 설명합니다.

  `mju_myiweb.StudentInfo` 클래스의 필드:


  ┌─────────────────────┬────────────────┬────────────────────────────────────────────┬────────────────────────────────────────────────────────┐
  │ 필드명              │ 타입           │ 설명                                       │ 예시 값                                                │
  ├─────────────────────┼────────────────┼────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
  │ student_id          │ str            │ 학번                                       │ "60222100"                                             │
  │ name_korean         │ str            │ 한글 성명                                  │ "신년기"                                               │
  │ name_english_first    │ str            │ 영문 성 (Last Name)                        │ "Shin"                                                 │
  │ name_english_last     │ str            │ 영문 이름 (First Name)                     │ "Nyeon Ki"                                             │
  │ grade               │ str            │ 학년                                       │ "4" (학년 숫자만, "4 학년"에서 파싱됨)                 │
  │ status              │ str            │ 학적 상태 (재학, 휴학 등)                  │ "재학"                                                 │
  │ department          │ str            │ 학부(과)명                                 │ "(반도체·ICT대학) 컴퓨터정보통신공학부 컴퓨터공학전공" │
  │ advisor             │ str            │ 상담 교수                                  │ "조민경 (컴퓨터정보통신공학부 컴퓨터공학전공)"         │
  │ design_advisor      │ str            │ 학생설계전공지도교수                       │ " ()" (정보가 없으면 빈 괄호 포함)                     │
  │ phone               │ str            │ 전화번호                                   │ "010-9503-1512"                                        │
  │ mobile              │ str            │ 휴대폰 번호                                │ "01095031512"                                          │
  │ email               │ str            │ 이메일 주소                                │ "sygys10293@mju.ac.kr"                                 │
  │ current_zip         │ str            │ 현 거주지 우편번호                         │ "136-29"                                               │
  │ current_address1    │ str            │ 현 거주지 주소 1 (기본 주소)               │ "경기도 성남시 분당구 미금일로 22"                     │
  │ current_address2    │ str            │ 현 거주지 주소 2 (상세 주소)               │ "208동 204호"                                          │
  │ registered_zip      │ str            │ 주민등록 주소 우편번호                     │ "136-29"                                               │
  │ registered_address1 │ str            │ 주민등록 주소 1 (기본 주소)                │ "경기도 성남시 분당구 미금일로 22"                     │
  │ registered_address2 │ str            │ 주민등록 주소 2 (상세 주소)                │ "208동 204호"                                          │
  │ photo_base64        │ str            │ 학생 사진 (JPEG, Base64 인코딩)            │ "/9j/4AAQSkZJRgABAgAA... (생략)"                       │
  │ focus_newsletter    │ bool           │ 명지포커스 책자 수신 동의 여부             │ True 또는 False                                        │
  │ raw_data            │ Dict[str, Any] │ 파싱된 원본 데이터를 Key-Value 형태로 저장 │ {'학번': '60222100', '한글성명': '신년기', ...}        │
  └─────────────────────┴────────────────┴────────────────────────────────────────────┴────────────────────────────────────────────────────────┘
유틸리티 메서드:

   * to_dict() -> Dict[str, Any]: StudentInfo 객체의 내용을 JSON 직렬화가 용이한 딕셔너리 형태로 반환합니다. 이 메서드는 API 응답에서 사용될 것입니다.
   * print_summary() -> None: 콘솔에 학생 정보 요약을 보기 좋게 출력합니다. (라이브러리 사용 시 디버깅 또는 간단한 정보 확인용)
  ---

  2. Docker 기반 API 서버

  다른 프로그래밍 언어에서도 쉽게 사용할 수 있도록, HTTP 기반의 RESTful API를 제공하고 Docker로
  패키징하는 방식을 제안합니다. Python 기반이므로 FastAPI 프레임워크를 사용하는 것이 성능과 개발
  편의성 면에서 가장 이상적입니다.

  API 정의서

  엔드포인트: POST /api/v1/student-card

  설명: 사용자의 학번과 비밀번호를 받아 명지대학교 학생 정보를 조회합니다.

  Request Body (`application/json`):

   1 {
   2   "user_id": "YOUR_STUDENT_ID",
   3   "password": "YOUR_PASSWORD"
   4 }

  Success Response (`200 OK`):

   * 성공 시, StudentInfo 객체의 to_dict() 메서드가 반환하는 것과 동일한 구조의 JSON 객체를
     반환합니다.

    1 {
    2   "student_id": "60221234",
    3   "name_korean": "홍길동",
    4   "name_english": "GIL DONG HONG",
    5   "grade": "4",
    6   "status": "재학",
    7   "department": "(반도체·ICT대학) 컴퓨터정보통신공학부 컴퓨터공학전공",
    8   "advisor": "조민경 (컴퓨터정보통신공학부 컴퓨터공학전공)",
    9   "design_advisor": " ()",
   10   "phone": "010-1234-5678",
   11   "mobile": "01012345678",
   12   "email": "test@mju.ac.kr",
   13   "current_address": {
   14     "zip": "123-45",
   15     "address1": "경기도 용인시 처인구 명지로 116",
   16     "address2": "창조예술관"
   17   },
   18   "registered_address": {
   19     "zip": "123-45",
   20     "address1": "경기도 용인시 처인구 명지로 116",
   21     "address2": "창조예술관"
   22   },
   23   "photo_base64": "/9j/4AAQSkZJRgABAg... (truncated)",
   24   "focus_newsletter": false
   25 }

  Error Responses:

   * `401 Unauthorized`: 아이디 또는 비밀번호가 잘못되었을 때

   1     {
   2       "detail": "아이디 또는 비밀번호가 틀렸습니다."
   3     }

   * `502 Bad Gateway`: 학교 서버 접속 불가 등 네트워크 문제 발생 시

   1     {
   2       "detail": "학교 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
   3     }

  설계 설명

   * RESTful 원칙: POST 메서드를 사용하여 리소스를 조회하는 이유는, 민감한 정보(비밀번호)를 URL
     파라미터가 아닌 Request Body에 담아 보내기 위함입니다.
   * 표준화된 JSON: 요청과 응답 모두 표준 JSON 형식을 사용하여 언어에 구애받지 않고 쉽게 연동할 수
     있습니다.
   * 상태 코드 활용: HTTP 상태 코드(200, 401, 502 등)를 통해 요청의 성공/실패 여부를 명확히
     전달합니다.
   * Dockerization: Dockerfile을 작성하여 FastAPI 애플리케이션을 실행 환경과 함께 패키징합니다.
     이를 통해 어떤 서버 환경에서든 docker run 명령 한 줄로 쉽게 서버를 배포할 수 있습니다.
   * 이미지 처리: 이 방식에서도 이미지는 Base64 문자열로 JSON 페이로드에 포함하는 것이 가장
     효율적입니다. 클라이언트는 이 문자열을 받아 각자의 환경에 맞게 이미지로 디코딩하여 사용하면
     됩니다.

  공통 고민사항: 이미지 처리

  제안하신 것처럼 두 시나리오 모두에서 Base64 인코딩된 문자열로 이미지를 처리하는 것이 가장 좋은
  방법입니다.

   * 이유 1: 의존성 없음
       * 이미지 데이터를 반환하기 위해 별도의 파일 저장소나 이미지 URL을 관리할 필요가 없습니다.
         모든 데이터가 하나의 응답(객체 또는 JSON)에 포함됩니다.
   * 이유 2: 유연성
       * 라이브러리/API 사용자는 받은 Base64 문자열을 가지고 파일로 저장, 웹페이지에 바로 표시(<img
         src="data:image/jpeg;base64,...">), 메모리 내에서 이미지 처리 등 원하는 작업을 자유롭게
         수행할 수 있습니다.
   * 이유 3: 표준
       * API에서 바이너리 데이터를 텍스트 기반 형식(JSON)에 포함시키는 매우 일반적이고 표준적인
         방법입니다.

 2. API 에러 응답 확장 (라이브러리 자체 오류 포함)

  기존에 제안했던 401 Unauthorized, 502 Bad Gateway 외에, 라이브러리 내부에서 발생할 수 있는 추가적인 오류들에 대한 응답을 정의합니다.

  추가되는 Error Responses:

   * `400 Bad Request`: 잘못된 요청 파라미터가 전달되었을 때 (예: 필수 필드 누락 등)

   1     {
   2       "detail": "요청 본문 형식이 올바르지 않거나 필수 필드가 누락되었습니다."
   3     }

   * `401 Unauthorized`:
       * InvalidCredentialsError: 학번 또는 비밀번호가 잘못되었을 때
   1         {
   2           "detail": "아이디 또는 비밀번호가 틀렸습니다."
   3         }
       * SessionExpiredError: 로그인 세션이 만료되어 재인증이 필요할 때 (이론적으로 API에서는 거의 발생하지 않지만, 라이브러리 내부에서 세션 만료를 감지했을 경우)
   1         {
   2           "detail": "로그인 세션이 만료되었습니다. 다시 시도해주세요."
   3         }

   * `500 Internal Server Error`:
       * PageParsingError: MSI 웹 페이지 구조 변경 등으로 인해 라이브러리가 학생 정보를 올바르게 파싱하지 못할 때

   1         {
   2           "detail": "내부 서버 오류: 학생 정보 페이지 파싱에 실패했습니다. (학교 시스템 변경 가능성)"
   3         }
       * MyIWebError (General Library Error): 위에 명시된 것 외의 예상치 못한 라이브러리 내부 오류 발생 시

   1         {
   2           "detail": "내부 서버 오류: 알 수 없는 라이브러리 문제가 발생했습니다."
   3         }
       * 기타 서버 측에서 발생할 수 있는 예외 (FastAPI 애플리케이션의 일반적인 오류)

   1         {
   2           "detail": "내부 서버 오류가 발생했습니다."
   3         }

   * `502 Bad Gateway`:
       * NetworkError: 학교 서버에 접속할 수 없을 때 (방화벽, 서버 다운 등)

   1         {
   2           "detail": "학교 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
   3         }

  FastAPI 예외 처리 전략:

  FastAPI를 사용한다면 HTTPException을 사용하여 이러한 오류 응답을 쉽게 처리할 수 있습니다. 예를 들어:

    1 from fastapi import FastAPI, HTTPException, status
    2 from mju_univ_auth import StudentInfo
    3 from mju_univ_auth.exceptions import (
    4     InvalidCredentialsError, NetworkError, PageParsingError, MyIWebError, SessionExpiredError
    5 )
    6
    7 app = FastAPI()
    8
    9 # ... (요청 모델 정의 등)
   10
   11 @app.post("/api/v1/student-card")
   12 async def get_student_card(credentials: LoginCredentials): # LoginCredentials는 Pydantic 모델
   13     try:
   14         student_info = StudentInfo.from_login(
   15             user_id=credentials.user_id,
   16             user_pw=credentials.password
   17         )
   18         return student_info.to_dict()
   19     except InvalidCredentialsError:
   20         raise HTTPException(
   21             status_code=status.HTTP_401_UNAUTHORIZED,
   22             detail="아이디 또는 비밀번호가 틀렸습니다."
   23         )
   25     except SessionExpiredError:
   26         raise HTTPException(
   27             status_code=status.HTTP_401_UNAUTHORIZED,
   28             detail="로그인 세션이 만료되었습니다. 다시 시도해주세요."
   29         )
   30     except NetworkError:
   31         raise HTTPException(
   32             status_code=status.HTTP_502_BAD_GATEWAY,
   33             detail="학교 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
   34         )
   35     except PageParsingError:
   36         raise HTTPException(
   37             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
   38             detail="내부 서버 오류: 학생 정보 페이지 파싱에 실패했습니다. (학교 시스템 변경 가능성)"
   39         )
   40     except MyIWebError as e:
   41         # 기타 예상치 못한 라이브러리 오류
   42         raise HTTPException(
   43             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
   44             detail=f"내부 서버 오류: 라이브러리 오류 - {e}"
   45         )
   46     except Exception:
   47         # 모든 잡지 못한 예외 처리
   48         raise HTTPException(
   49             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
   50             detail="예상치 못한 서버 오류가 발생했습니다."
   51         )

  이 상세화된 정의와 응답 전략은 라이브러리 사용자와 API 클라이언트 모두에게 더 명확하고 견고한 경험을 제공할 것입니다.



  이 계획안을 바탕으로 실제 코드 수정을 진행하시면, 사용성과 확장성 측면에서 매우 만족스러운
  결과물을 만드실 수 있을 것입니다. 다음 단계로 진행할 준비가 되시면 알려주세요.