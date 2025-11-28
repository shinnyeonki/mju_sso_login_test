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

load_dotenv()
USER_ID = os.getenv('MJU_ID', '').strip()
USER_PW = os.getenv('MJU_PW', '').strip()

if not USER_ID or not USER_PW:
    print("Error: .env 파일을 확인해주세요.")
    exit()

def get_session_data_via_selenium():
    print(">>> [1/4] Headless 브라우저 시작...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 아래 옵션들이 봇 탐지를 피하는 데 도움을 줍니다
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # 로그인 페이지 접속
        login_url = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp"
        driver.get(login_url)
        
        wait = WebDriverWait(driver, 15)
        
        print(">>> [2/4] 로그인 정보 입력...")
        id_input = wait.until(EC.presence_of_element_located((By.ID, "input-userId")))
        id_input.clear()
        id_input.send_keys(USER_ID)
        
        pw_input = driver.find_element(By.ID, "input-password")
        pw_input.clear()
        pw_input.send_keys(USER_PW)
        
        login_btn = driver.find_element(By.CSS_SELECTOR, "button.login_bt")
        login_btn.click()
        
        # LMS 페이지 로딩 대기
        wait.until(EC.url_contains("lms.mju.ac.kr"))
        print(f">>> [3/4] 로그인 성공! (Selenium URL: {driver.current_url})")
        
        # [핵심] 현재 브라우저의 쿠키와 User-Agent를 모두 가져옵니다.
        selenium_cookies = driver.get_cookies()
        user_agent = driver.execute_script("return navigator.userAgent;")
        
        cookie_dict = {c['name']: c['value'] for c in selenium_cookies}
        
        return cookie_dict, user_agent

    except Exception as e:
        print(f">>> [오류] Selenium 과정 실패: {e}")
        return None, None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # 1. 셀레니움으로 쿠키와 UA 획득
    cookies, ua = get_session_data_via_selenium()
    
    if cookies and ua:
        print(f"\n>>> [Transfer] User-Agent 동기화: {ua[:30]}...")
        print(f">>> [Transfer] 쿠키 개수: {len(cookies)}")
        
        # 2. Requests 세션 설정 (완벽한 동기화)
        session = requests.Session()
        session.cookies.update(cookies)
        session.headers.update({
            'User-Agent': ua,  # Selenium과 동일한 UA 사용
            'Referer': 'https://lms.mju.ac.kr/' # LMS 내부 접근인 척 설정
        })
        
        # 3. 데이터 요청
        print(">>> [4/4] Requests로 데이터 요청 시작")
        target_url = "https://lms.mju.ac.kr/ilos/main/main_form.acl"
        res = session.get(target_url)
        
        print(f"응답 코드: {res.status_code}")
        print(f"최종 URL: {res.url}")
        
        # 검증 로직
        if "로그아웃" in res.text or "Logout" in res.text:
            print("\n>>> [최종 성공] Requests로 LMS 권한 획득 완료!")
            print("이제 session 객체를 사용하여 크롤링을 진행하시면 됩니다.")
        else:
            print("\n>>> [최종 실패] 여전히 세션이 유지되지 않았습니다.")
            # 실패 시 어디로 튕겼는지 확인
            if "sso.mju.ac.kr" in res.url:
                print("이유: 세션이 끊겨서 다시 SSO 로그인 페이지로 리다이렉트 되었습니다.")
    else:
        print(">>> Selenium 로그인 단계에서 실패했습니다.")