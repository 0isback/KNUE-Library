import requests


def get_seat_urls(seat_number):
    """사용자가 원하는 좌석 번호에 대한 API 요청 URL 반환"""
    if not (1 <= seat_number <= 150):
        raise ValueError("좌석 번호는 1부터 150까지 입력해야 합니다.")

    seat_id = 724 + seat_number
    return {
        "check": f"https://eris.knue.ac.kr/smufu-api/seat/{seat_id}/check-chargeable",
        "reserve": f"https://eris.knue.ac.kr/smufu-api/api/mo/seats/{seat_id}/charge-temporarily"
    }


def login(session, login_id, password):
    """로그인 요청 및 pyxis-auth-token 반환"""
    login_url = "https://lib.knue.ac.kr/pyxis-api/api/login"
    login_data = {
        "loginId": login_id,
        "password": password,
        "isMobile": True,
        "isFamilyLogin": False,
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    }

    response = session.post(login_url, headers=headers, json=login_data)

    try:
        response_data = response.json()
        if response_data.get("success"):
            print("로그인 성공!")
            return response_data.get("data", {}).get("accessToken")
        else:
            print("로그인 실패:", response_data.get("message"))
            return None
    except requests.exceptions.JSONDecodeError:
        print("서버 응답이 JSON 형식이 아닙니다. 응답 내용:", response.text)
        return None


def check_current_ticket(session, headers):
    """현재 예약된 좌석 정보 확인"""
    ticket_url = "https://eris.knue.ac.kr/smufu-api/api/mo/my-ticket"
    response = session.get(ticket_url, headers=headers)

    try:
        ticket_data = response.json()
        if ticket_data.get("success") and ticket_data.get("data", {}).get("list"):
            seat_info = ticket_data["data"]["list"][0]
            return {
                "seat_num": seat_info["seat"]["code"],  # 예약된 좌석 번호
                "seat_ID": seat_info["seat"]["id"],  # 예약된 좌석 ID
                "charge_ID": seat_info["id"]  # charge ID
            }
        else:
            print("현재 대여 중인 좌석이 없습니다.")
            return None
    except requests.exceptions.JSONDecodeError:
        print("좌석 확인 응답이 JSON 형식이 아닙니다.")
        return None


def reserve_seat(session, headers, seat_number):
    """원하는 좌석 예약"""
    urls = get_seat_urls(seat_number)

    # 좌석 사용 가능 여부 확인
    check_response = session.get(urls["check"], headers=headers)
    try:
        check_data = check_response.json()
        if not check_data.get("data", {}).get("isChargeable", False):
            print(f"{seat_number}번 좌석은 이미 사용 중입니다.")
            return None
    except requests.exceptions.JSONDecodeError:
        print("좌석 확인 응답이 JSON 형식이 아닙니다.")
        return None

    # 좌석 예약 시도
    reserve_response = session.post(urls["reserve"], headers=headers)
    try:
        reserve_data = reserve_response.json()
        print(reserve_data)
        seat_charge_id = reserve_data.get("data", {}).get("id")

        if seat_charge_id:
            confirm_url = f"https://eris.knue.ac.kr/smufu-api/api/mo/seat-charge/{seat_charge_id}/confirm"
            confirm_response = session.post(confirm_url, headers=headers)
            confirm_data = confirm_response.json()

            if confirm_data.get("success"):
                print(f"{seat_number}번 좌석 예약 성공!")
                return seat_charge_id  # 성공한 경우 charge_id 반환
            else:
                print("예약 확인 실패:", confirm_data.get("message"))
        else:
            print("좌석 예약 실패:", reserve_data.get("message"))
    except requests.exceptions.JSONDecodeError:
        print("좌석 예약 응답이 JSON 형식이 아닙니다.")

    return None


def return_seat(session, headers, seat_charge_id):
    """현재 예약된 좌석을 반납"""
    if not seat_charge_id:
        print("반납할 좌석이 없습니다.")
        return False

    return_url = f'https://eris.knue.ac.kr/smufu-api/api/mo/seat-charge/{seat_charge_id}/return'
    return_response = session.post(return_url, headers=headers)

    try:
        return_data = return_response.json()
        if return_data.get("success"):
            print("좌석 반납 성공!")
            return True
        else:
            print("좌석 반납 실패:", return_data.get("message"))
    except requests.exceptions.JSONDecodeError:
        print("반납 응답이 JSON 형식이 아닙니다.")

    return False


# ✅ 메인 실행 로직
if __name__ == "__main__":
    session = requests.Session()
    login_id = "아이디"  # 아이디 입력
    password = "비밀번호"  # 비밀번호 입력

    # 로그인 진행
    access_token = login(session, login_id, password)

    if access_token:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "pyxis-auth-token": access_token
        }

        # 현재 예약된 좌석 확인
        current_seat = check_current_ticket(session, headers)

        # 선호 좌석 번호 (예: 140번 좌석)
        preferred_seat = 140

        if current_seat:
            current_seat_num = int(current_seat["seat_num"])
            current_seat_charge_id = current_seat["charge_ID"]

            if current_seat_num != preferred_seat:
                # 현재 좌석이 선호 좌석과 다르면 반납 후 예약
                print(f"{current_seat_num}번 좌석을 반납하고 {preferred_seat}번 좌석을 예약합니다.")
                return_seat(session, headers, current_seat_charge_id)

                # 반납 후 예약
                if reserve_seat(session, headers, preferred_seat):
                    print(f"새로운 좌석 {preferred_seat}번 예약 완료!")
            else:
                print("현재 좌석이 이미 선호 좌석입니다.")
        else:
            # 예약된 좌석이 없으면 바로 예약 진행
            if reserve_seat(session, headers, preferred_seat):
                print(f"새로운 좌석 {preferred_seat}번 예약 완료!")
