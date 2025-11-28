"""
메인 실행 모듈
=============
MSI 로그인 후 학생카드 정보 조회 전체 흐름 제어
"""

import os
import json
import logging
import argparse
from dotenv import load_dotenv

from .utils import setup_logging, get_logger, Colors
from .sso import MJUSSOLogin
from .student_card import StudentCardFetcher, StudentInfo


# 모듈 로거
logger = get_logger(__name__)


def fetch_student_info(user_id: str = None, user_pw: str = None) -> StudentInfo:
    """
    학생 정보 조회 메인 함수
    
    Args:
        user_id: 학번 (None이면 환경변수에서 로드)
        user_pw: 비밀번호 (None이면 환경변수에서 로드)
    
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
        logger.error(".env 파일에서 MJU_ID, MJU_PW를 찾을 수 없습니다.")
        print("\n.env 파일 형식:")
        print("  MJU_ID=학번")
        print("  MJU_PW=비밀번호")
        return None
    
    logger.info(f"""
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
    sso = MJUSSOLogin(user_id, user_pw)
    result = sso.login(service='msi')
    
    if not result.success:
        logger.error(f"로그인 실패: {result.message}")
        return None
    
    # Step 2: 학생카드 정보 조회
    fetcher = StudentCardFetcher(result.session, user_pw)
    student_info = fetcher.fetch()
    
    if student_info:
        student_info.print_summary()
        return student_info
    else:
        logger.error("학생 정보 조회에 실패했습니다.")
        return None


def main():
    """CLI 메인 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description='명지대학교 학생카드 정보 조회 프로그램',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
로깅 레벨 설명:
  DEBUG    - 모든 상세 정보 출력 (HTTP 요청/응답, 암호화 과정 등)
  INFO     - 주요 단계별 진행 상황 출력 (기본값)
  WARNING  - 경고 메시지만 출력
  ERROR    - 에러 메시지만 출력

사용 예:
  python -m myiweb.main                    # INFO 레벨로 실행
  python -m myiweb.main -v                 # DEBUG 레벨로 실행 (상세 모드)
  python -m myiweb.main --log-level DEBUG  # DEBUG 레벨로 실행
  python -m myiweb.main -q                 # WARNING 레벨로 실행 (조용한 모드)
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='상세 로그 출력 (DEBUG 레벨)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='조용한 모드 (WARNING 레벨)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='로깅 레벨 설정 (기본값: INFO)'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='색상 출력 비활성화'
    )
    
    args = parser.parse_args()
    
    # 로깅 레벨 결정 (우선순위: -v > -q > --log-level)
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARNING
    else:
        log_level = getattr(logging, args.log_level)
    
    # 로깅 설정 초기화
    setup_logging(level=log_level, use_colors=not args.no_color)
    
    logger.info(f"로깅 레벨: {logging.getLevelName(log_level)}")
    
    student_info = fetch_student_info()
    
    if student_info:
        logger.info("="*70)
        logger.info(" 최종 결과")
        logger.info("="*70)
        logger.info("✓ 학생 정보 조회 완료!")
        
        # JSON 형태로 출력
        print(f"\n{Colors.BOLD}[JSON 출력]{Colors.END}")
        print(json.dumps(student_info.to_dict(), ensure_ascii=False, indent=2))
    else:
        logger.info("="*70)
        logger.info(" 실패")
        logger.info("="*70)
        logger.error("✗ 학생 정보를 조회할 수 없습니다.")


if __name__ == "__main__":
    main()
