"""
myiweb 통합 클라이언트
====================
SSO 로그인을 처리하고, 다양한 서비스(Fetcher) 객체를 생성하는 메인 클라이언트.
"""
from typing import Optional
import requests

from .sso import MJUSSOLogin
from .student_card import StudentCardService
from .student_changelog import StudentChangeLogService
from .exceptions import MyIWebError


class Client:
    """
    myiweb의 메인 클라이언트.
    이 클래스를 통해 로그인하고, 원하는 정보 조회를 위한 서비스 객체를 얻습니다.
    """

    def __init__(self, user_id: str, user_pw: str, verbose: bool = True):
        """
        클라이언트 생성 시 SSO 로그인을 수행합니다.

        Args:
            user_id: 학번
            user_pw: 비밀번호
            verbose: 상세 로그 출력 여부

        Raises:
            MyIWebError: 로그인 과정에서 발생하는 모든 예외
        """
        self._user_id = user_id
        self._user_pw = user_pw
        self._verbose = verbose
        self._session: Optional[requests.Session] = None

        try:
            if self._verbose:
                print("=" * 70)
                print(" MyIWeb Client 초기화: SSO 로그인을 시작합니다.")
                print("=" * 70)

            sso = MJUSSOLogin(self._user_id, self._user_pw, self._verbose)
            self._session = sso.login(service='msi')

        except MyIWebError as e:
            # 로그인 실패 시 클라이언트 초기화 실패로 간주하고 예외를 다시 발생시킴
            raise MyIWebError(f"클라이언트 초기화 실패(로그인 실패): {e}") from e

    def student_card(self) -> 'StudentCardService':
        """
        학생카드(StudentCard) 정보를 조회할 수 있는 서비스 객체를 반환합니다.

        Returns:
            StudentCardService: 학생카드 조회 서비스 객체
        """
        if not self._session:
            raise MyIWebError("클라이언트가 성공적으로 초기화되지 않았습니다. (세션 없음)")
        return StudentCardService(self._session, self._user_pw, self._verbose)

    def student_change_log(self) -> 'StudentChangeLogService':
        """
        학적변동내역(StudentChangeLog) 정보를 조회할 수 있는 서비스 객체를 반환합니다.

        Returns:
            StudentChangeLogService: 학적변동내역 조회 서비스 객체
        """
        if not self._session:
            raise MyIWebError("클라이언트가 성공적으로 초기화되지 않았습니다. (세션 없음)")
        return StudentChangeLogService(self._session, self._user_pw, self._verbose)

# 순환 참조 방지를 위해 타입 힌트만 있는 클래스들을 임포트
# 실제로는 myiweb/__init__.py 에서 최종적으로 조합됨
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .student_card import StudentCardService
    from .student_changelog import StudentChangeLogService
