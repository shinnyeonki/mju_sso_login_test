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


def fetch_student_info(user_id: str = None, user_pw: str = None, verbose: bool = True) -> StudentInfo:
    """
    학생 정보 조회 메인 함수
    
    Args:
        user_id: 학번 (None이면 환경변수에서 로드)
        user_pw: 비밀번호 (None이면 환경변수에서 로드)
        verbose: 상세 로그 출력 여부
    
    Returns:
        StudentInfo: 학생 정보 객체 (실패 시 None)
    """
    # 환경변수 로드
    load_dotenv()
    
    if not user_id:
        user_id = os.getenv('MJU_ID', '').strip()
    if not user_pw:
        user_pw = os.getenv('MJU_PW', '').strip()
    
    if not user_id or not user_pw:
        log_error(".env 파일에서 MJU_ID, MJU_PW를 찾을 수 없습니다.")
        print("\n.env 파일 형식:")
        print("  MJU_ID=학번")
        print("  MJU_PW=비밀번호")
        return None
    
    if verbose:
        print(f"""
{Colors.BOLD}{Colors.HEADER}
╔══════════════════════════════════════════════════════════════════════╗
║                명지대학교 학생카드 정보 조회 프로그램                        ║
║                                                                      ║
║  이 프로그램은 MSI에 로그인하여 학생 정보를 조회합니다.                        ║
║  - Step 1: SSO 로그인 (RSA + AES-256 암호화, PBKDF2 키 파생)             ║
║  - Step 2: MSI 세션 설정 (JavaScript 폼 자동 제출)                        ║
║  - Step 3: 학생카드 페이지 접속 (sideform POST)                          ║
║  - Step 4: 비밀번호 재인증                                               ║
║  - Step 5: 학생 정보 파싱                                                ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.END}
""")
    
    # Step 1: MSI 로그인 (SSO 인증 + MSI 세션 설정 완료)
    sso = MJUSSOLogin(user_id, user_pw, verbose=verbose)
    result = sso.login(service='msi')
    
    if not result.success:
        log_error(f"로그인 실패: {result.message}")
        return None
    
    # Step 2: 학생카드 정보 조회
    fetcher = StudentCardFetcher(result.session, user_pw, verbose=verbose)
    student_info = fetcher.fetch()
    
    if student_info:
        if verbose:
            student_info.print_summary()
        return student_info
    else:
        log_error("학생 정보 조회에 실패했습니다.")
        return None


def main():
    """CLI 메인 함수"""
    student_info = fetch_student_info(verbose=True)
    
    if student_info:
        log_section("최종 결과")
        log_success("학생 정보 조회 완료!")
        
        # JSON 형태로 출력
        print(f"\n{Colors.BOLD}[JSON 출력]{Colors.END}")
        print(json.dumps(student_info.to_dict(), ensure_ascii=False, indent=2))
    else:
        log_section("실패")
        log_error("학생 정보를 조회할 수 없습니다.")


if __name__ == "__main__":
    main()
