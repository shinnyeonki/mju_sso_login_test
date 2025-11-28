"""
메인 실행 모듈
=============
MSI 로그인 후 학생카드 정보 조회 전체 흐름 제어
"""

import os
import json
from dotenv import load_dotenv

from .utils import Colors, log_section, log_success, log_error
from .sso import MJUSSOLogin
from .student_card import StudentCardFetcher, StudentInfo
from .exceptions import MyIWebError


def fetch_student_info(user_id: str, user_pw: str, verbose: bool = True) -> StudentInfo:
    """
    학생 정보 조회 메인 함수 (순수 API)
    
    Args:
        user_id: 학번
        user_pw: 비밀번호
        verbose: 상세 로그 출력 여부
    
    Returns:
        StudentInfo: 학생 정보 객체
        
    Raises:
        MyIWebError: 학생 정보 조회 과정에서 발생하는 모든 예외의 기본 클래스
    """
    # Step 1: MSI 로그인 (SSO 인증 + MSI 세션 설정 완료)
    sso = MJUSSOLogin(user_id, user_pw, verbose=verbose)
    session = sso.login(service='msi')
    
    # Step 2: 학생카드 정보 조회
    fetcher = StudentCardFetcher(session, user_pw, verbose=verbose)
    student_info = fetcher.fetch()
    
    if student_info:
        if verbose:
            student_info.print_summary()
        return student_info
    
    # fetcher.fetch()가 None을 반환하는 경우는 없지만, 안정성을 위해 남겨둠
    raise MyIWebError("알 수 없는 이유로 학생 정보 조회에 실패했습니다.")


def main():
    """CLI 메인 함수"""
    # 환경변수 로드
    load_dotenv()
    
    user_id = os.getenv('MJU_ID', '').strip()
    user_pw = os.getenv('MJU_PW', '').strip()
    
    # CLI 배너 출력
    banner = (
        f"\n{Colors.BOLD}{Colors.HEADER}\n"
        "╔══════════════════════════════════════════════════════════════════════╗\n"
        "║                명지대학교 학생카드 정보 조회 프로그램                        ║\n"
        "║                                                                      ║\n"
        "║  이 프로그램은 MSI에 로그인하여 학생 정보를 조회합니다.                        ║\n"
        "║  - Step 1: SSO 로그인 (RSA + AES-256 암호화, PBKDF2 키 파생)             ║\n"
        "║  - Step 2: MSI 세션 설정 (JavaScript 폼 자동 제출)                        ║\n"
        "║  - Step 3: 학생카드 페이지 접속 (sideform POST)                          ║\n"
        "║  - Step 4: 비밀번호 재인증                                               ║\n"
        "║  - Step 5: 학생 정보 파싱                                                ║\n"
        "╚══════════════════════════════════════════════════════════════════════╝\n"
        f"{Colors.END}\n"
    )
    print(banner)
    
    if not user_id or not user_pw:
        log_error(".env 파일에서 MJU_ID, MJU_PW를 찾을 수 없습니다.")
        print("\n.env 파일 형식:")
        print("  MJU_ID=학번")
        print("  MJU_PW=비밀번호")
        return
    
    try:
        student_info = fetch_student_info(user_id, user_pw, verbose=False)
        
        log_section("최종 결과")
        log_success("학생 정보 조회 완료!")
        
        # JSON 형태로 출력
        print(f"\n{Colors.BOLD}[JSON 출력]{Colors.END}")
        print(json.dumps(student_info.to_dict(), ensure_ascii=False, indent=2))
        
    except MyIWebError as e:
        log_section("실패")
        log_error(str(e))


if __name__ == "__main__":
    main()