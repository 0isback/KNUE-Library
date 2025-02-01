- 메인 실행 로직에서 login_id 에는 사용자 아이디를, password 에는 사용자 비밀번호를 입력합니다.
- preferred_seat 값에 선호하는 좌석 번호를 입력합니다. (1번 ~ 150번)

* 본 프로그램의 기능은 다음과 같습니다.
  - 사용자가 예약한 좌석이 존재하지 않는 경우: preferred_seat 값에 해당하는 좌석 번호로 reserve_seat 실행
  - 사용자가 예약한 좌석이 존재하는 경우:
    예약한 좌석이 preferred_seat 값과 같으면, 실행하지 않음
    예약한 좌석이 preferred_seat 값과 다르면, 예약한 좌석을 반납하고 reserve_seat 실행
