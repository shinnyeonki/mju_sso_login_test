"""
사용 예제
========
myiweb 모듈을 사용하여 학생 정보를 조회하는 예제

사용법:
1. .env 파일에 MJU_ID와 MJU_PW 설정
2. python -m myiweb.examples 실행
"""

import os
import sys
import json
from dotenv import load_dotenv

# 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from myiweb import MJUSSOLogin, StudentCardFetcher, StudentInfo, MyIWebError
from myiweb.utils import log_info, log_success, log_error


def example_low_level():
    """
    저수준(Low-level) API 사용 예제
    - 각 과정을 직접 제어해야 할 때 유용합니다.
    """
    print("\n=== 저수준 API 예제 ===\n")
    load_dotenv()
    
    user_id = os.getenv('MJU_ID')
    user_pw = os.getenv('MJU_PW')
    
    if not user_id or not user_pw:
        log_error("Skipping low-level example: .env 파일에 MJU_ID와 MJU_PW를 설정해주세요.")
        return
    
    try:
        # 1. MSI 로그인
        log_info("Step 1", "SSO 로그인 시도...")
        sso = MJUSSOLogin(user_id, user_pw, verbose=False)
        session = sso.login(service='msi')
        log_success("로그인 성공!")
        
        # 2. 학생카드 정보 조회
        log_info("Step 2", "학생카드 정보 조회 시도...")
        fetcher = StudentCardFetcher(session, user_pw, verbose=False)
        student_info = fetcher.fetch()
        log_success("학생카드 정보 조회 성공!")
        
        # 3. 결과 출력
        print("\n--- 학생 정보 요약 ---")
        print(f"학번: {student_info.student_id}")
        print(f"이름: {student_info.name_korean}")
        print(f"학과: {student_info.department}")
        print("----------------------\n")

    except MyIWebError as e:
        log_error(f"저수준 API 테스트 실패: {e}")


def example_high_level():
    """
    고수준(High-level) API 사용 예제
    - 가장 권장되는 사용법입니다.
    """
    print("\n=== 고수준 API 예제 (가장 권장) ===\n")
    load_dotenv()
    
    user_id = os.getenv('MJU_ID')
    user_pw = os.getenv('MJU_PW')

    if not user_id or not user_pw:
        log_error("Skipping high-level example: .env 파일에 MJU_ID와 MJU_PW를 설정해주세요.")
        return
    
    try:
        # 단 한 줄의 클래스 메서드 호출로 모든 과정을 처리합니다.
        log_info("API Call", "StudentInfo.from_login(user_id, user_pw) 호출...")
        info = StudentInfo.from_login(user_id, user_pw, verbose=False)
        log_success("고수준 API 호출 성공!")
        
        # 결과를 딕셔너리로 변환하여 JSON으로 출력
        data = info.to_dict()
        
        print("\n--- JSON 출력 ---")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("-------------------\n")

    except MyIWebError as e:
        log_error(f"고수준 API 테스트 실패: {e}")


def example_services():
    """다양한 서비스 로그인 예제"""
    print("\n=== 다양한 서비스 로그인 테스트 예제 ===\n")
    load_dotenv()
    
    user_id = os.getenv('MJU_ID')
    user_pw = os.getenv('MJU_PW')

    if not user_id or not user_pw:
        log_error("Skipping services example: .env 파일에 MJU_ID와 MJU_PW를 설정해주세요.")
        return
    
    # 지원되는 서비스 목록
    services = ['lms', 'portal', 'msi', 'myicap', 'library']
    
    for service in services:
        try:
            sso = MJUSSOLogin(user_id, user_pw, verbose=False)
            sso.login(service=service)
            log_success(f"✓ {service} 로그인 성공")
        except MyIWebError as e:
            log_error(f"✗ {service} 로그인 실패: {e}")


if __name__ == "__main__":
    example_high_level()
    example_low_level()
    example_services()

