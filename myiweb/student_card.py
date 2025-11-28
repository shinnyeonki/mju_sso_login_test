"""
학생카드 정보 조회 모듈
=======================
MSI 서비스에서 학생카드 정보를 조회하고 파싱

학생카드 페이지 접근 과정:
1. MSI 홈페이지에서 CSRF 토큰 추출
2. sideform 방식으로 /servlet/su/sum/Sum00Svl01getStdCard POST
3. 비밀번호 재입력 (보안 인증) - 평문으로 /servlet/sys/sys15/Sys15Svl01verifyPW POST
4. 리다이렉트 폼 처리 (JavaScript onLoad 폼 자동 제출 대체)
5. 학생 정보 HTML 파싱
"""

import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup, SoupStrainer

from .utils import (
    Colors, log_section, log_step, log_info, log_success, log_error, 
    log_warning, log_request, log_response
)


@dataclass
class StudentInfo:
    """학생 정보 데이터 클래스"""
    # 기본 정보
    student_id: str = ""           # 학번
    name_korean: str = ""          # 한글성명
    name_english_first: str = ""   # 영문성명(성)
    name_english_last: str = ""    # 영문성명(이름)
    
    # 학적 정보
    grade: str = ""                # 학년
    status: str = ""               # 학적상태 (재학, 휴학 등)
    department: str = ""           # 학부(과)
    advisor: str = ""              # 상담교수
    design_advisor: str = ""       # 학생설계전공지도교수
    
    # 연락처 정보
    phone: str = ""                # 전화번호
    mobile: str = ""               # 휴대폰
    email: str = ""                # 이메일
    
    # 주소 정보
    current_zip: str = ""          # 현거주지 우편번호
    current_address1: str = ""     # 현거주지 주소1
    current_address2: str = ""     # 현거주지 주소2
    registered_zip: str = ""       # 주민등록 우편번호
    registered_address1: str = ""  # 주민등록 주소1
    registered_address2: str = ""  # 주민등록 주소2
    
    # 사진 (Base64)
    photo_base64: str = ""
    
    # 기타
    focus_newsletter: bool = False  # 명지포커스 수신여부
    
    # 원본 데이터 (딕셔너리)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'student_id': self.student_id,
            'name_korean': self.name_korean,
            'name_english': f"{self.name_english_first} {self.name_english_last}".strip(),
            'grade': self.grade,
            'status': self.status,
            'department': self.department,
            'advisor': self.advisor,
            'design_advisor': self.design_advisor,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': self.email,
            'current_address': {
                'zip': self.current_zip,
                'address1': self.current_address1,
                'address2': self.current_address2,
            },
            'registered_address': {
                'zip': self.registered_zip,
                'address1': self.registered_address1,
                'address2': self.registered_address2,
            },
            'photo_base64': self.photo_base64[:50] + '...' if self.photo_base64 else '',
            'focus_newsletter': self.focus_newsletter,
        }
    
    def print_summary(self) -> None:
        """학생 정보 요약 출력"""
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f" 학생 정보 조회 결과")
        print(f"{'='*60}{Colors.END}")
        
        print(f"\n{Colors.BOLD}[기본 정보]{Colors.END}")
        log_info("학번", self.student_id)
        log_info("한글성명", self.name_korean)
        log_info("영문성명", f"{self.name_english_first} {self.name_english_last}")
        
        print(f"\n{Colors.BOLD}[학적 정보]{Colors.END}")
        log_info("학년", self.grade)
        log_info("학적상태", self.status)
        log_info("학부(과)", self.department)
        log_info("상담교수", self.advisor)
        if self.design_advisor:
            log_info("학생설계전공지도교수", self.design_advisor)
        
        print(f"\n{Colors.BOLD}[연락처]{Colors.END}")
        log_info("전화번호", self.phone)
        log_info("휴대폰", self.mobile)
        log_info("E-Mail", self.email)
        
        print(f"\n{Colors.BOLD}[주소]{Colors.END}")
        log_info("현거주지", f"({self.current_zip}) {self.current_address1} {self.current_address2}")
        log_info("주민등록", f"({self.registered_zip}) {self.registered_address1} {self.registered_address2}")
        
        if self.photo_base64:
            print(f"\n{Colors.BOLD}[사진]{Colors.END}")
            log_info("사진 데이터", f"Base64 ({len(self.photo_base64)} chars)")


class StudentCardFetcher:
    """학생카드 정보 조회 클래스"""
    
    MSI_HOME_URL = "https://msi.mju.ac.kr/servlet/security/MySecurityStart"
    STUDENT_CARD_URL = "https://msi.mju.ac.kr/servlet/su/sum/Sum00Svl01getStdCard"
    PASSWORD_VERIFY_URL = "https://msi.mju.ac.kr/servlet/sys/sys15/Sys15Svl01verifyPW"
    
    def __init__(self, session: requests.Session, user_pw: str, verbose: bool = True):
        """
        Args:
            session: 로그인된 requests 세션
            user_pw: 비밀번호 (2차 인증용)
            verbose: 상세 로그 출력 여부
        """
        self.session = session
        self.user_pw = user_pw
        self.verbose = verbose
        
        # CSRF 토큰
        self.csrf_token: Optional[str] = None
        self._last_url: Optional[str] = None
    
    def _extract_csrf_from_html(self, html: str) -> Optional[str]:
        """HTML에서 CSRF 토큰 추출"""
        # meta 태그에서 추출
        csrf_match = re.search(r'meta[^>]*_csrf[^>]*content="([^"]+)"', html)
        if csrf_match:
            return csrf_match.group(1)
        
        # X-CSRF-TOKEN 헤더 설정에서 추출
        csrf_match = re.search(r"X-CSRF-TOKEN['\"]?\s*:\s*['\"]([^'\"]+)['\"]", html)
        if csrf_match:
            return csrf_match.group(1)
        
        # input hidden에서 추출
        csrf_match = re.search(r'name="_csrf"\s+value="([^"]+)"', html)
        if csrf_match:
            return csrf_match.group(1)
        
        return None
    
    def _get_csrf_token(self) -> bool:
        """MSI 홈페이지에서 CSRF 토큰 추출"""
        if self.verbose:
            log_step("1", "CSRF 토큰 추출")
            log_request('GET', self.MSI_HOME_URL)
        
        try:
            response = self.session.get(self.MSI_HOME_URL, timeout=10)
            
            if self.verbose:
                log_response(response, show_body=False)
            
            # SSO로 리다이렉트되면 세션 만료
            if 'sso.mju.ac.kr' in response.url:
                log_error("세션이 만료되었습니다. 다시 로그인해주세요.")
                return False
            
            self.csrf_token = self._extract_csrf_from_html(response.text)
            
            if not self.csrf_token:
                log_error("CSRF 토큰을 찾을 수 없습니다.")
                return False
            
            if self.verbose:
                log_info("CSRF Token", self.csrf_token)
                log_success("CSRF 토큰 추출 완료")
            
            return True
            
        except requests.RequestException as e:
            log_error(f"CSRF 토큰 추출 실패: {e}")
            return False
    
    def _access_student_card_page(self) -> Optional[str]:
        """sideform 방식으로 학생카드 페이지 접근"""
        if self.verbose:
            log_step("2", "학생카드 페이지 접근 (sideform 방식)")
        
        # sideform 데이터
        form_data = {
            'sysdiv': 'SCH',
            'subsysdiv': 'SCH',
            'folderdiv': '101',
            'pgmid': 'W_SUD005',
            'userFlag': '1',
            '_csrf': self.csrf_token,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://msi.mju.ac.kr',
            'Referer': self.MSI_HOME_URL,
            'X-CSRF-TOKEN': self.csrf_token,
        }
        
        if self.verbose:
            log_request('POST', self.STUDENT_CARD_URL, headers, form_data)
        
        try:
            response = self.session.post(
                self.STUDENT_CARD_URL,
                data=form_data,
                headers=headers,
                timeout=15
            )
            
            if self.verbose:
                log_response(response, show_body=False)
            
            self._last_url = response.url
            return response.text
            
        except requests.RequestException as e:
            log_error(f"학생카드 페이지 접근 실패: {e}")
            return None
    
    def _check_password_required(self, html: str) -> bool:
        """비밀번호 입력이 필요한지 확인"""
        return 'tfpassword' in html or 'verifyPW' in html
    
    def _submit_password(self, html: str) -> Optional[str]:
        """
        비밀번호 제출 - 평문으로 전송
        
        폼 구조:
        <form name="form1" action="/servlet/sys/sys15/Sys15Svl01verifyPW" method="post">
            <input type="hidden" name="originalurl" value="https://msi.mju.ac.kr/servlet/su/sum/Sum00Svl01getStdCard">
            <input type="password" name="tfpassword">
            <input type="hidden" name="_csrf" value="...">
        </form>
        """
        if self.verbose:
            log_step("3", "비밀번호 인증")
        
        # originalurl 추출
        original_match = re.search(r'name="originalurl"\s+value="([^"]+)"', html)
        original_url = original_match.group(1) if original_match else self.STUDENT_CARD_URL
        
        # 폼 데이터 준비 - 평문 비밀번호 전송
        form_data = {
            'originalurl': original_url,
            'tfpassword': self.user_pw,
            '_csrf': self.csrf_token,
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://msi.mju.ac.kr',
            'Referer': self._last_url or self.STUDENT_CARD_URL,
            'X-CSRF-TOKEN': self.csrf_token,
        }
        
        if self.verbose:
            safe_data = {k: ('****' if 'password' in k.lower() else v) for k, v in form_data.items()}
            log_request('POST', self.PASSWORD_VERIFY_URL, headers, safe_data)
        
        try:
            response = self.session.post(
                self.PASSWORD_VERIFY_URL,
                data=form_data,
                headers=headers,
                timeout=15
            )
            
            if self.verbose:
                log_response(response, show_body=False)
            
            self._last_url = response.url
            return response.text
            
        except requests.RequestException as e:
            log_error(f"비밀번호 인증 실패: {e}")
            return None
    
    def _handle_redirect_form(self, html: str) -> Optional[str]:
        """
        JavaScript 리다이렉트 폼 처리
        
        비밀번호 인증 성공 후 자동으로 제출되는 폼:
        <form name="form1" action="https://msi.mju.ac.kr/servlet/su/sum/Sum00Svl01getStdCard">
            <input type="hidden" name="_csrf" value="...">
        </form>
        <script>
        $(document).ready(function(){
            var frm = document.form1;
            frm.action = "...";
            frm.submit();
        });
        </script>
        """
        if self.verbose:
            log_step("4", "리다이렉트 폼 처리")
        
        # 정규표현식으로 빠르게 추출 시도
        action_match = re.search(r'frm\.action\s*=\s*["\']([^"\']+)["\']', html)
        if not action_match:
            action_match = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', html)
        
        csrf_match = re.search(r'name=["\']_csrf["\'][^>]*value=["\']([^"\']+)["\']', html)
        if not csrf_match:
            csrf_match = re.search(r'value=["\']([^"\']+)["\'][^>]*name=["\']_csrf["\']', html)
        
        action = action_match.group(1) if action_match else ''
        
        if not action or 'Sum00Svl01getStdCard' not in action:
            return html
        
        csrf = csrf_match.group(1) if csrf_match else self.csrf_token
        
        # 정규표현식으로 못 찾은 경우 lxml로 폴백
        if not action_match or not csrf_match:
            parse_only = SoupStrainer('form')
            soup = BeautifulSoup(html, 'lxml', parse_only=parse_only)
            form = soup.find('form')
        
            if form:
                if not action:
                    action = form.get('action', '')
                    action_js = re.search(r'frm\.action\s*=\s*["\']([^"\']+)["\']', html)
                    if action_js:
                        action = action_js.group(1)
                if not csrf_match:
                    csrf_input = form.find('input', {'name': '_csrf'})
                    csrf = csrf_input.get('value') if csrf_input else self.csrf_token
            
            if not action or 'Sum00Svl01getStdCard' not in action:
                return html
        
        if self.verbose:
            log_info("Redirect URL", action)
        
        # 폼 제출
        form_data = {'_csrf': csrf}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://msi.mju.ac.kr',
            'Referer': self._last_url,
            'X-CSRF-TOKEN': csrf,
        }
        
        try:
            response = self.session.post(
                action,
                data=form_data,
                headers=headers,
                timeout=15
            )
            
            if self.verbose:
                log_response(response, show_body=False)
            
            return response.text
            
        except requests.RequestException as e:
            log_error(f"리다이렉트 폼 처리 실패: {e}")
            return None
    
    def _parse_student_info(self, html: str) -> Optional[StudentInfo]:
        """학생 정보 HTML 파싱"""
        if self.verbose:
            log_step("5", "학생 정보 파싱")
        
        # 필요한 태그만 파싱 (img, div, input)
        parse_only = SoupStrainer(['img', 'div', 'input'])
        soup = BeautifulSoup(html, 'lxml', parse_only=parse_only)
        info = StudentInfo()
        
        # 사진 추출
        img_tag = soup.find('img', src=re.compile(r'^data:image'))
        if img_tag:
            src = img_tag.get('src', '')
            # data:image/jpg;base64,... 형식에서 base64 부분만 추출
            if 'base64,' in src:
                info.photo_base64 = src.split('base64,')[1]
        
        # flex-table-item 요소들에서 정보 추출
        for item in soup.find_all('div', class_='flex-table-item'):
            title_div = item.find('div', class_='item-title')
            data_div = item.find('div', class_='item-data')
            
            if not title_div or not data_div:
                continue
            
            title = title_div.get_text(strip=True)
            
            # input 필드에서 값 추출
            input_field = data_div.find('input')
            if input_field:
                value = input_field.get('value', '')
            else:
                # div 내 텍스트에서 값 추출
                inner_div = data_div.find('div')
                value = inner_div.get_text(strip=True) if inner_div else data_div.get_text(strip=True)
            
            # 필드 매핑
            info.raw_data[title] = value
            
            if title == '학번':
                info.student_id = value
            elif title == '한글성명':
                info.name_korean = value
            elif title == '영문성명(성)':
                info.name_english_first = value
            elif title == '영문성명(이름)':
                info.name_english_last = value
            elif title == '학년':
                info.grade = value.replace('학년', '').strip()
            elif title == '학적상태':
                info.status = value
            elif title == '학부(과)':
                info.department = value
            elif title == '상담교수':
                info.advisor = value
            elif title == '학생설계전공지도교수':
                info.design_advisor = value
            elif title == '전화번호' or '전화번호' in title:
                input_tel = data_div.find('input', {'name': 'std_tel'})
                if input_tel:
                    info.phone = input_tel.get('value', '')
                else:
                    info.phone = value
            elif title == '휴대폰':
                input_htel = data_div.find('input', {'name': 'htel'})
                if input_htel:
                    info.mobile = input_htel.get('value', '')
                else:
                    info.mobile = value
            elif title == 'E-Mail':
                input_email = data_div.find('input', {'name': 'email'})
                if input_email:
                    info.email = input_email.get('value', '')
                else:
                    info.email = value
            elif '현거주지' in title:
                # 우편번호
                zip1 = data_div.find('input', {'name': 'zip1'})
                zip2 = data_div.find('input', {'name': 'zip2'})
                if zip1 and zip2:
                    info.current_zip = f"{zip1.get('value', '')}-{zip2.get('value', '')}"
                elif zip1:
                    info.current_zip = zip1.get('value', '')
                # 주소
                addr1 = data_div.find('input', {'name': 'addr1'})
                addr2 = data_div.find('input', {'name': 'addr2'})
                if addr1:
                    info.current_address1 = addr1.get('value', '')
                if addr2:
                    info.current_address2 = addr2.get('value', '')
            elif '주민등록' in title:
                # 우편번호
                zip1_2 = data_div.find('input', {'name': 'zip1_2'})
                zip2_2 = data_div.find('input', {'name': 'zip2_2'})
                if zip1_2 and zip2_2:
                    info.registered_zip = f"{zip1_2.get('value', '')}-{zip2_2.get('value', '')}"
                elif zip1_2:
                    info.registered_zip = zip1_2.get('value', '')
                # 주소
                addr1_2 = data_div.find('input', {'name': 'addr1_2'})
                addr2_2 = data_div.find('input', {'name': 'addr2_2'})
                if addr1_2:
                    info.registered_address1 = addr1_2.get('value', '')
                if addr2_2:
                    info.registered_address2 = addr2_2.get('value', '')
            elif '명지포커스' in title:
                checkbox = data_div.find('input', {'name': 'focus_yn'})
                if checkbox:
                    info.focus_newsletter = checkbox.get('checked') is not None
        
        # 필수 정보 확인
        if not info.student_id:
            log_error("학생 정보를 찾을 수 없습니다.")
            return None
        
        if self.verbose:
            log_success("학생 정보 파싱 완료")
        
        return info
    
    def fetch(self) -> Optional[StudentInfo]:
        """학생카드 정보 조회"""
        if self.verbose:
            log_section("학생카드 정보 조회")
        
        # Step 1: CSRF 토큰 추출
        if not self._get_csrf_token():
            return None
        
        # Step 2: 학생카드 페이지 접근 (sideform 방식)
        html = self._access_student_card_page()
        if not html:
            return None
        
        # Step 3: 비밀번호 인증 필요 여부 확인
        if self._check_password_required(html):
            if self.verbose:
                log_warning("비밀번호 인증이 필요합니다.")
            
            # 비밀번호 제출
            html = self._submit_password(html)
            if not html:
                return None
            
            # Step 4: 리다이렉트 폼 처리
            html = self._handle_redirect_form(html)
            if not html:
                return None
            
            # 여전히 비밀번호 인증 필요하면 실패
            if self._check_password_required(html):
                log_error("비밀번호 인증에 실패했습니다.")
                return None
        
        # Step 5: 학생 정보 파싱
        info = self._parse_student_info(html)
        
        return info
