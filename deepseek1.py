import requests

# 1. 초기 요청을 통해 JSESSIONID를 가져오기
initial_url = 'https://lib.knue.ac.kr/umobile/'
session = requests.Session()
initial_response = session.get(initial_url)

# 초기 요청에서 받은 쿠키를 확인
cookies = session.cookies.get_dict()
print("Initial Cookies:", cookies)

# 2. 로그인 요청 보내기
login_url = 'https://lib.knue.ac.kr/pyxis-api/api/login'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ko',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://lib.knue.ac.kr',
    'Pragma': 'no-cache',
    'Referer': 'https://lib.knue.ac.kr/umobile/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

json_data = {
    'loginId': '아이디',
    'password': '비밀번호',
    'isMobile': True,
    'isFamilyLogin': False,
}

# 세션을 사용하여 로그인 요청 보내기
login_response = session.post(login_url, headers=headers, json=json_data)

if login_response.status_code == 200:  # 로그인 성공 시
    login_data = login_response.json()
    access_token = login_data['data']['accessToken']  # accessToken 값 추출

    # headers 딕셔너리에 'pyxis-auth-token' 추가
    headers['pyxis-auth-token'] = access_token

    # 사용자로부터 좌석 번호 입력 받기
    seat_number = int(input("좌석 번호를 입력하세요 (예: 122): "))  # 예: 122
    unique_value = seat_number + 724  # 고유 값 계산 (122 + 724 = 846)

    # 첫 번째 단계: GET 요청
    check_url = f'https://eris.knue.ac.kr/smufu-api/seat/{unique_value}/check-chargeable'
    check_response = requests.get(check_url, headers=headers)

    # GET 요청 결과 확인
    if check_response.status_code == 200:
        print(f"좌석 {seat_number} (고유 값: {unique_value})의 상태 확인 결과:")
        print(check_response.json())
    else:
        print(f"좌석 상태 확인 실패. 상태 코드: {check_response.status_code}")

    # 두 번째 단계: POST 요청 (임시 예약)
    charge_url = f'https://eris.knue.ac.kr/smufu-api/api/mo/seats/{unique_value}/charge-temporarily'
    charge_response = requests.post(charge_url, headers=headers)

    # POST 요청 결과 확인
    if charge_response.status_code == 200:
        print(f"좌석 {seat_number} (고유 값: {unique_value}) 임시 예약 결과:")
        print(charge_response.json())
    else:
        print(f"임시 예약 실패. 상태 코드: {charge_response.status_code}")
else:
    print("Login failed with status code:", login_response.status_code)
