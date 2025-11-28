"""
명지대학교 My iWeb 모듈
=====================
MSI(My iWeb) 서비스에 접속하여 학생 정보를 조회하는 모듈

모듈 구성:
- exceptions: 커스텀 예외 클래스
- utils: 로깅 및 공통 유틸리티
- crypto: RSA/AES 암호화 유틸리티
- sso: SSO 로그인 클래스
- student_card: 학생카드 정보 조회
- main: 메인 실행 및 고수준 API
"""

from .main import fetch_student_info
from .sso import MJUSSOLogin
from .student_card import StudentCardFetcher, StudentInfo
from .exceptions import (
    MyIWebError,
    NetworkError,
    PageParsingError,
    InvalidCredentialsError,
    SessionExpiredError
)

__all__ = [
    # 고수준 API 함수
    'fetch_student_info',
    
    # 핵심 클래스
    'MJUSSOLogin',
    'StudentCardFetcher',
    'StudentInfo',
    
    # 예외 클래스
    'MyIWebError',
    'NetworkError',
    'PageParsingError',
    'InvalidCredentialsError',
    'SessionExpiredError',
]