"""
사용 예제
========
myiweb 모듈을 사용하여 학생 정보를 조회하는 예제

사용법:
1. .env 파일에 MJU_ID와 MJU_PW 설정
2. python -m myiweb 실행

또는 Python 코드에서 직접 사용:
>>> from myiweb import fetch_student_info
>>> info = fetch_student_info()
>>> print(info.to_dict())
"""

import os
import sys

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from myiweb import MJUSSOLogin, StudentCardFetcher, StudentInfo
from myiweb import log_section, log_info, log_success, log_error
from dotenv import load_dotenv


def example_basic():
    """기본 사용 예제"""
    load_dotenv()
    
    user_id = os.getenv('MJU_ID')
    user_pw = os.getenv('MJU_PW')
    
    if not user_id or not user_pw:
        print("Error: .env 파일에 MJU_ID와 MJU_PW를 설정해주세요.")
        return
    
    # 1. MSI 로그인
    sso = MJUSSOLogin(user_id, user_pw)
    result = sso.login(service='msi')
    
    if not result.success:
        print(f"로그인 실패: {result.message}")
        return
    
    print("로그인 성공!")
    
    # 2. 학생카드 정보 조회
    fetcher = StudentCardFetcher(result.session, user_pw)
    student_info = fetcher.fetch()
    
    if student_info:
        print("\n=== 학생 정보 ===")
        print(f"학번: {student_info.student_id}")
        print(f"이름: {student_info.name_korean}")
        print(f"학년: {student_info.grade}")
        print(f"학과: {student_info.department}")
        print(f"이메일: {student_info.email}")
    else:
        print("학생 정보 조회 실패")


def example_with_dict():
    """딕셔너리로 변환 예제"""
    from myiweb.main import fetch_student_info
    
    # 간단한 함수로 조회
    info = fetch_student_info(verbose=False)
    
    if info:
        # 딕셔너리로 변환
        data = info.to_dict()
        
        import json
        print(json.dumps(data, ensure_ascii=False, indent=2))


def example_services():
    """다양한 서비스 로그인 예제"""
    load_dotenv()
    
    user_id = os.getenv('MJU_ID')
    user_pw = os.getenv('MJU_PW')
    
    # 지원되는 서비스 목록
    services = ['lms', 'portal', 'msi', 'myicap', 'library']
    
    for service in services:
        sso = MJUSSOLogin(user_id, user_pw, verbose=False)
        result = sso.login(service=service)
        
        status = "✓" if result.success else "✗"
        print(f"{status} {service}: {result.message}")


if __name__ == "__main__":
    print("=== 기본 사용 예제 ===\n")
    example_basic()
