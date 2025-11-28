import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 1. 환경변수 로드
load_dotenv()
USER_ID = os.getenv('MJU_ID')
USER_PW = os.getenv('MJU_PW')

if not USER_ID or not USER_PW:
    print("Error: .env 파일에 아이디/비밀번호가 설정되지 않았습니다.")
    exit()

# 2. 브라우저 설정 (옵션)
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # 브라우저 창을 띄우지 않으려면 주석 해제
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# 자동화 탐지 방지 (선택사항)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

# 3. 브라우저 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 타겟 로그인 URL (제공해주신 URL)
    login_url = "https://sso.mju.ac.kr/sso/auth?response_type=code&client_id=lms&state=Random%20String&redirect_uri=https://lms.mju.ac.kr/ilos/sso/sso_response.jsp"
    
    print(">>> 로그인 페이지 접속 중...")
    driver.get(login_url)

    # 4. 요소 대기 및 입력 (명시적 대기 사용)
    wait = WebDriverWait(driver, 10)
    
    # 아이디 입력창 찾기 및 입력 (#input-userId)
    id_input = wait.until(EC.presence_of_element_located((By.ID, "input-userId")))
    id_input.clear()
    id_input.send_keys(USER_ID)

    # 비밀번호 입력창 찾기 및 입력 (#input-password)
    pw_input = driver.find_element(By.ID, "input-password")
    pw_input.clear()
    pw_input.send_keys(USER_PW)

    # 로그인 버튼 클릭 (폼 제출)
    login_btn = driver.find_element(By.CSS_SELECTOR, "button.login_bt")
    login_btn.click()
    
    print(">>> 로그인 정보 전송 완료. 리다이렉트 대기 중...")

    # 5. 로그인 성공 확인
    # 성공하면 LMS 페이지(lms.mju.ac.kr)로 이동하므로 URL이 바뀔 때까지 대기
    # 혹은 특정 요소가 뜰 때까지 대기해도 됨
    wait.until(EC.url_contains("lms.mju.ac.kr"))
    
    print(">>> 로그인 성공!")
    print(f"현재 URL: {driver.current_url}")

    # 6. 세션 쿠키 추출 (이후 requests 등에서 사용 가능)
    cookies = driver.get_cookies()
    
    # 쿠키를 딕셔너리 형태로 변환 (requests 라이브러리용)
    session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
    print(">>> 획득한 쿠키:", session_cookies)
    
    # 여기서부터는 requests를 사용하여 데이터를 가져올 수 있습니다.
    # 예: import requests; res = requests.get('https://lms.mju.ac.kr/...', cookies=session_cookies)

    # 확인을 위해 잠시 대기
    time.sleep(3)

except Exception as e:
    print(f"Error 발생: {e}")

finally:
    driver.quit()