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
- __main__: `python -m myiweb`을 위한 CLI 엔트리포인트
"""

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
    # 고수준 API 클래스
    'StudentInfo',
    
    # 저수준 API 클래스 (내부 로직 접근용)
    'MJUSSOLogin',
    'StudentCardFetcher',
    
    # 예외 클래스
    'MyIWebError',
    'NetworkError',
    'PageParsingError',
    'InvalidCredentialsError',
    'SessionExpiredError',
]