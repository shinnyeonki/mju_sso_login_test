"""
명지대학교 SSO 로그인 및 학생카드 정보 조회 (Selenium 버전)
=========================================================
- Headless Chrome을 사용하여 SSO 로그인
- MSI 학생정보시스템 접속 및 학생카드 조회
- 모든 과정을 Selenium으로 처리 (리다이렉션, JS 폼 자동제출 포함)
"""

import os
import re
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


# ==================== 데이터 클래스 ====================

@dataclass
class StudentInfo:
    """학생 정보 데이터 클래스"""
    student_id: str = ""
    name_korean: str = ""
    name_english_first: str = ""
    name_english_last: str = ""
    grade: str = ""
    status: str = ""
    department: str = ""
    advisor: str = ""
    design_advisor: str = ""
    phone: str = ""
    mobile: str = ""
    email: str = ""
    current_zip: str = ""
    current_address1: str = ""
    current_address2: str = ""
    registered_zip: str = ""
    registered_address1: str = ""
    registered_address2: str = ""
    photo_base64: str = ""
    focus_newsletter: bool = False
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def print_summary(self) -> None:
        """학생 정보 요약 출력"""
        print(f"\n{'='*60}")
        print(f" 학생 정보 조회 결과")
        print(f"{'='*60}")
        
        print(f"\n[기본 정보]")
        print(f"  학번: {self.student_id}")
        print(f"  한글성명: {self.name_korean}")
        print(f"  영문성명: {self.name_english_first} {self.name_english_last}")
        
        print(f"\n[학적 정보]")
        print(f"  학년: {self.grade}")
        print(f"  학적상태: {self.status}")
        print(f"  학부(과): {self.department}")
        print(f"  상담교수: {self.advisor}")
        if self.design_advisor:
            print(f"  학생설계전공지도교수: {self.design_advisor}")
        
        print(f"\n[연락처]")
        print(f"  전화번호: {self.phone}")
        print(f"  휴대폰: {self.mobile}")
        print(f"  E-Mail: {self.email}")
        
        print(f"\n[주소]")
        print(f"  현거주지: ({self.current_zip}) {self.current_address1} {self.current_address2}")
        print(f"  주민등록: ({self.registered_zip}) {self.registered_address1} {self.registered_address2}")
        
        if self.photo_base64:
            print(f"\n[사진]")
            print(f"  사진 데이터: Base64 ({len(self.photo_base64)} chars)")


# ==================== 메인 클래스 ====================

class MJUSeleniumClient:
    """명지대학교 Selenium 클라이언트 - SSO 로그인 및 학생카드 조회"""
    
    # URL 상수
    SSO_LOGIN_URL = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=msi&state=default&redirect_uri=https://msi.mju.ac.kr/servlet/security/MySecurityStart"
    MSI_HOME_URL = "https://msi.mju.ac.kr/servlet/security/MySecurityStart"
    STUDENT_CARD_MENU_SELECTOR = "학생카드"
    
    def __init__(self, user_id: str, user_pw: str, headless: bool = True, verbose: bool = True):
        self.user_id = user_id
        self.user_pw = user_pw
        self.headless = headless
        self.verbose = verbose
        self.driver: Optional[webdriver.Chrome] = None
    
    def _log(self, message: str):
        """로그 출력"""
        if self.verbose:
            print(message)
    
    def _init_driver(self) -> webdriver.Chrome:
        """Chrome WebDriver 초기화"""
        self._log(">>> [초기화] Chrome WebDriver 설정 중...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # navigator.webdriver 속성 제거 (봇 탐지 방지)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        return driver
    
    def login_sso(self) -> bool:
        """SSO 로그인 수행"""
        self._log("\n>>> [1/4] SSO 로그인 시작...")
        
        try:
            self.driver = self._init_driver()
            self.driver.get(self.SSO_LOGIN_URL)
            
            wait = WebDriverWait(self.driver, 15)
            
            # 아이디 입력
            self._log(">>> 아이디/비밀번호 입력 중...")
            id_input = wait.until(EC.presence_of_element_located((By.ID, "input-userId")))
            id_input.clear()
            id_input.send_keys(self.user_id)
            
            # 비밀번호 입력
            pw_input = self.driver.find_element(By.ID, "input-password")
            pw_input.clear()
            pw_input.send_keys(self.user_pw)
            
            # 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.CSS_SELECTOR, "button.login_bt")
            login_btn.click()
            
            # MSI 페이지로 이동할 때까지 대기
            self._log(">>> 로그인 처리 및 리다이렉션 대기 중...")
            wait.until(EC.url_contains("msi.mju.ac.kr"))
            
            # 페이지 로딩 완료 대기
            time.sleep(1)
            
            self._log(f">>> SSO 로그인 성공! (URL: {self.driver.current_url})")
            return True
            
        except TimeoutException:
            self._log(">>> [오류] 로그인 타임아웃 - 아이디/비밀번호를 확인하세요.")
            if self.driver:
                self.driver.save_screenshot("login_failed.png")
            return False
        except Exception as e:
            self._log(f">>> [오류] SSO 로그인 실패: {e}")
            if self.driver:
                self.driver.save_screenshot("login_error.png")
            return False
    
    def _navigate_to_student_card(self) -> bool:
        """학생카드 메뉴로 이동"""
        self._log("\n>>> [2/4] 학생카드 메뉴 접근...")
        
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # 학생카드 메뉴 클릭 (JavaScript로 sideform 제출하는 방식)
            # 실제 웹사이트에서 메뉴 클릭 시 JavaScript가 실행됨
            # sideform 방식: 숨겨진 폼에 pgmid 등을 설정하고 submit
            
            # 방법 1: 직접 JavaScript 실행으로 학생카드 페이지 접근
            js_code = """
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = '/servlet/su/sum/Sum00Svl01getStdCard';
            
            var fields = {
                'sysdiv': 'SCH',
                'subsysdiv': 'SCH', 
                'folderdiv': '101',
                'pgmid': 'W_SUD005',
                'userFlag': '1'
            };
            
            // CSRF 토큰 추가
            var csrfMeta = document.querySelector('meta[name="_csrf"]');
            if (csrfMeta) {
                fields['_csrf'] = csrfMeta.getAttribute('content');
            }
            
            for (var key in fields) {
                var input = document.createElement('input');
                input.type = 'hidden';
                input.name = key;
                input.value = fields[key];
                form.appendChild(input);
            }
            
            document.body.appendChild(form);
            form.submit();
            """
            
            self.driver.execute_script(js_code)
            
            # 페이지 전환 대기
            time.sleep(2)
            
            self._log(f">>> 학생카드 페이지 접근 완료 (URL: {self.driver.current_url})")
            return True
            
        except Exception as e:
            self._log(f">>> [오류] 학생카드 메뉴 접근 실패: {e}")
            return False
    
    def _handle_password_verification(self) -> bool:
        """2차 비밀번호 인증 처리"""
        self._log("\n>>> [3/4] 비밀번호 재인증...")
        
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # 비밀번호 입력 필드 확인
            try:
                pw_field = wait.until(EC.presence_of_element_located((By.NAME, "tfpassword")))
            except TimeoutException:
                # 비밀번호 필드가 없으면 이미 인증된 상태
                self._log(">>> 비밀번호 재인증 불필요")
                return True
            
            self._log(">>> 비밀번호 입력 중...")
            pw_field.clear()
            pw_field.send_keys(self.user_pw)
            
            # 현재 URL 저장 (변경 감지용)
            current_url = self.driver.current_url
            
            # 확인 버튼 클릭
            self._log(">>> 확인 버튼 클릭...")
            submit_btn = self.driver.find_element(By.ID, "submitpw")
            submit_btn.click()
            
            # URL이 변경되거나 학생카드 페이지가 로드될 때까지 대기
            self._log(">>> 페이지 전환 대기 중...")
            try:
                # URL이 verifyPW 또는 다른 페이지로 변경되기를 기다림
                wait.until(lambda driver: driver.current_url != current_url or 
                          'flex-table-item' in driver.page_source or
                          'Sum00Svl01getStdCard' in driver.page_source)
            except TimeoutException:
                self._log(">>> [경고] 페이지 전환 타임아웃")
            
            # 추가 대기 (리다이렉트 폼 처리)
            time.sleep(2)
            
            # 리다이렉트 폼이 있으면 처리
            # Selenium은 JavaScript를 자동 실행하므로 document.ready의 submit()도 실행됨
            # 하지만 혹시 안 되면 수동으로 처리
            page_source = self.driver.page_source
            
            # 학생카드 데이터가 이미 로드되었는지 확인
            if 'flex-table-item' in page_source and '학번' in page_source:
                self._log(">>> 학생카드 페이지 로드 완료")
                return True
            
            # 리다이렉트 폼이 있는지 확인하고 처리
            if 'Sum00Svl01getStdCard' in page_source and 'form' in page_source.lower():
                self._log(">>> 리다이렉트 폼 발견, 수동 처리 중...")
                self.driver.execute_script("""
                    var forms = document.querySelectorAll('form');
                    for (var i = 0; i < forms.length; i++) {
                        var form = forms[i];
                        var action = form.getAttribute('action') || '';
                        if (action.indexOf('Sum00Svl01getStdCard') !== -1) {
                            form.submit();
                            return;
                        }
                    }
                    // form1이 있으면 제출
                    if (document.form1) {
                        document.form1.submit();
                    }
                """)
                time.sleep(2)
            
            self._log(f">>> 현재 URL: {self.driver.current_url}")
            self._log(">>> 비밀번호 인증 완료")
            return True
            
        except Exception as e:
            self._log(f">>> [오류] 비밀번호 인증 실패: {e}")
            if self.driver:
                self.driver.save_screenshot("password_verify_failed.png")
            return False
    
    def _parse_student_info(self) -> Optional[StudentInfo]:
        """학생카드 페이지에서 정보 파싱"""
        self._log("\n>>> [4/4] 학생 정보 파싱...")
        
        try:
            # 페이지 로딩 대기
            time.sleep(2)
            
            # 디버깅: 현재 페이지 상태 확인
            self._log(f">>> 현재 URL: {self.driver.current_url}")
            
            page_source = self.driver.page_source
            
            # 학생카드 데이터가 있는지 확인 (flex-table-item과 학번)
            if 'flex-table-item' not in page_source or '학번' not in page_source:
                # 비밀번호 재인증 페이지인지 확인
                if 'tfpassword' in page_source and 'originalurl' in page_source:
                    self._log(">>> [경고] 아직 비밀번호 인증 페이지입니다.")
                    # 디버깅용 HTML 저장
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(page_source)
                    return None
                else:
                    self._log(">>> [경고] 학생카드 데이터를 찾을 수 없습니다.")
                    with open("debug_page.html", "w", encoding="utf-8") as f:
                        f.write(page_source)
                    return None
            
            info = StudentInfo()
            
            # 사진 추출
            try:
                img_elements = self.driver.find_elements(By.CSS_SELECTOR, "img[src^='data:image']")
                for img in img_elements:
                    src = img.get_attribute("src")
                    if src and "base64," in src:
                        info.photo_base64 = src.split("base64,")[1]
                        break
            except:
                pass
            
            # flex-table-item에서 정보 추출
            items = self.driver.find_elements(By.CSS_SELECTOR, ".flex-table-item")
            
            for item in items:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, ".item-title")
                    data_elem = item.find_element(By.CSS_SELECTOR, ".item-data")
                    
                    title = title_elem.text.strip()
                    
                    # input 필드에서 값 추출 시도
                    try:
                        input_field = data_elem.find_element(By.TAG_NAME, "input")
                        value = input_field.get_attribute("value") or ""
                    except NoSuchElementException:
                        # div 텍스트에서 추출
                        value = data_elem.text.strip()
                    
                    info.raw_data[title] = value
                    
                    # 필드 매핑
                    if title == "학번":
                        info.student_id = value
                    elif title == "한글성명":
                        info.name_korean = value
                    elif title == "영문성명(성)":
                        info.name_english_first = value
                    elif title == "영문성명(이름)":
                        info.name_english_last = value
                    elif title == "학년":
                        info.grade = value.replace("학년", "").strip()
                    elif title == "학적상태":
                        info.status = value
                    elif title == "학부(과)":
                        info.department = value
                    elif title == "상담교수":
                        info.advisor = value
                    elif title == "학생설계전공지도교수":
                        info.design_advisor = value
                    elif "전화번호" in title:
                        try:
                            tel_input = data_elem.find_element(By.NAME, "std_tel")
                            info.phone = tel_input.get_attribute("value") or ""
                        except:
                            info.phone = value
                    elif title == "휴대폰":
                        try:
                            htel_input = data_elem.find_element(By.NAME, "htel")
                            info.mobile = htel_input.get_attribute("value") or ""
                        except:
                            info.mobile = value
                    elif title == "E-Mail":
                        try:
                            email_input = data_elem.find_element(By.NAME, "email")
                            info.email = email_input.get_attribute("value") or ""
                        except:
                            info.email = value
                    elif "현거주지" in title:
                        try:
                            zip1 = data_elem.find_element(By.NAME, "zip1").get_attribute("value") or ""
                            zip2 = data_elem.find_element(By.NAME, "zip2").get_attribute("value") or ""
                            info.current_zip = f"{zip1}-{zip2}" if zip2 else zip1
                        except:
                            pass
                        try:
                            info.current_address1 = data_elem.find_element(By.NAME, "addr1").get_attribute("value") or ""
                        except:
                            pass
                        try:
                            info.current_address2 = data_elem.find_element(By.NAME, "addr2").get_attribute("value") or ""
                        except:
                            pass
                    elif "주민등록" in title:
                        try:
                            zip1 = data_elem.find_element(By.NAME, "zip1_2").get_attribute("value") or ""
                            zip2 = data_elem.find_element(By.NAME, "zip2_2").get_attribute("value") or ""
                            info.registered_zip = f"{zip1}-{zip2}" if zip2 else zip1
                        except:
                            pass
                        try:
                            info.registered_address1 = data_elem.find_element(By.NAME, "addr1_2").get_attribute("value") or ""
                        except:
                            pass
                        try:
                            info.registered_address2 = data_elem.find_element(By.NAME, "addr2_2").get_attribute("value") or ""
                        except:
                            pass
                    elif "명지포커스" in title:
                        try:
                            checkbox = data_elem.find_element(By.NAME, "focus_yn")
                            info.focus_newsletter = checkbox.is_selected()
                        except:
                            pass
                            
                except NoSuchElementException:
                    continue
            
            if not info.student_id:
                self._log(">>> [경고] 학번을 찾을 수 없습니다.")
                # 디버깅용 HTML 저장
                with open("debug_student_card.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                self._log(">>> 디버깅용 HTML 저장: debug_student_card.html")
                return None
            
            self._log(">>> 학생 정보 파싱 완료")
            return info
            
        except Exception as e:
            self._log(f">>> [오류] 학생 정보 파싱 실패: {e}")
            return None
    
    def fetch_student_card(self) -> Optional[StudentInfo]:
        """학생카드 정보 조회 (전체 프로세스)"""
        try:
            # Step 1: SSO 로그인
            if not self.login_sso():
                return None
            
            # Step 2: 학생카드 페이지 이동
            if not self._navigate_to_student_card():
                return None
            
            # Step 3: 비밀번호 재인증
            if not self._handle_password_verification():
                return None
            
            # Step 4: 학생 정보 파싱
            return self._parse_student_info()
            
        finally:
            self.close()
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None


# ==================== 환경변수 및 메인 ====================

load_dotenv()
USER_ID = os.getenv('MJU_ID', '').strip()
USER_PW = os.getenv('MJU_PW', '').strip()

if not USER_ID or not USER_PW:
    print("Error: .env 파일에 MJU_ID, MJU_PW를 설정해주세요.")
    exit()


if __name__ == "__main__":
    print("=" * 60)
    print(" 명지대학교 학생카드 정보 조회 (Selenium)")
    print("=" * 60)
    
    client = MJUSeleniumClient(
        user_id=USER_ID,
        user_pw=USER_PW,
        headless=True,  # True: 창 안 띄움, False: 브라우저 창 표시
        verbose=True
    )
    
    student_info = client.fetch_student_card()
    
    if student_info:
        student_info.print_summary()
        print("\n>>> 학생카드 정보 조회 완료!")
    else:
        print("\n>>> 학생카드 정보 조회 실패")