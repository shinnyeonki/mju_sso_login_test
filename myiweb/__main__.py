"""
명지대학교 My iWeb 모듈 실행 엔트리포인트 (CLI)
==============================================
`python -m myiweb` 명령으로 실행됩니다.
"""

import os
import json
from dotenv import load_dotenv

from .student_card import StudentInfo
from .exceptions import MyIWebError
from .utils import Colors, log_section, log_success, log_error


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
        # 새로운 고수준 API 사용
        student_info = StudentInfo.from_login(user_id, user_pw, verbose=True)
        
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