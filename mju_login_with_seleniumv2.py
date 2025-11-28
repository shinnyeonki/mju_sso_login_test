import os
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 1. 환경변수 설정
load_dotenv()
USER_ID = os.getenv('MJU_ID', '').strip()
USER_PW = os.getenv('MJU_PW', '').strip()

if not USER_ID or not USER_PW:
    print("Error: .env 파일을 확인해주세요.")
    exit()

def get_session_cookies_via_selenium():
    print(">>> [1/3] Headless 브라우저 시작...")
    
    # 브라우저 옵션 설정 (창 안 뜨게 & 속도 최적화)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 창 안 띄움
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    # 봇 탐지 방지 User-Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # 로그인 페이지 접속
        login_url = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp"
        driver.get(login_url)
        
        wait = WebDriverWait(driver, 10)
        
        print(">>> [2/3] 로그인 정보 입력 및 암호화 자동 수행...")
        # 아이디 입력
        id_input = wait.until(EC.presence_of_element_located((By.ID, "input-userId")))
        id_input.clear()
        id_input.send_keys(USER_ID)
        
        # 비밀번호 입력
        pw_input = driver.find_element(By.ID, "input-password")
        pw_input.clear()
        pw_input.send_keys(USER_PW)
        
        # 로그인 버튼 클릭 (이때 JS가 암호화를 수행함)
        login_btn = driver.find_element(By.CSS_SELECTOR, "button.login_bt")
        login_btn.click()
        
        # LMS 페이지로 이동할 때까지 대기 (로그인 성공 판단)
        wait.until(EC.url_contains("lms.mju.ac.kr"))
        print(f">>> [3/3] 로그인 성공! (URL: {driver.current_url})")
        
        # 쿠키 추출
        selenium_cookies = driver.get_cookies()
        
        # requests용 쿠키 딕셔너리로 변환
        cookie_dict = {c['name']: c['value'] for c in selenium_cookies}
        return cookie_dict

    except Exception as e:
        print(f">>> [오류] Selenium 로그인 실패: {e}")
        # 실패 시 스크린샷 저장 (디버깅용)
        driver.save_screenshot("login_failed.png")
        return None
        
    finally:
        driver.quit()

# === 메인 실행 로직 ===
if __name__ == "__main__":
    # 1. 셀레니움으로 인증 토큰(쿠키) 획득
    cookies = get_session_cookies_via_selenium()
    
    if cookies:
        print("\n>>> [Requests] 고속 데이터 수집 시작")
        
        # 2. 획득한 쿠키를 requests 세션에 심기
        session = requests.Session()
        session.cookies.update(cookies)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 3. 이제부터는 Selenium 없이 requests로 매우 빠르게 통신 가능
        lms_main = session.get("https://lms.mju.ac.kr/ilos/main/main_form.acl")
        
        if "로그아웃" in lms_main.text or "Logout" in lms_main.text:
            print(">>> [최종 검증] Requests로 LMS 접근 성공!")
            # 예: 강의 목록 가져오기 등 추가 작업 수행
        else:
            print(">>> [최종 검증] 접근 실패 (세션 문제)")
    else:
        print(">>> 로그인을 완료하지 못했습니다.")