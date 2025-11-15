# 파일명: main_gui.py
# 목적: 사용자가 목표 온도를 설정하면 AI가 자동으로 팬 속도를 예측하는 시뮬레이터
# 비유: 자동차의 '크루즈 컨트롤'처럼, 목표를 정하면 시스템이 알아서 조절

import customtkinter as ctk  # 현대적인 GUI를 만드는 라이브러리
import joblib  # AI 모델 파일을 불러오는 도구
import numpy as np  # 수학 계산용 라이브러리
from tkinter import messagebox  # 팝업 메시지 창
import os

# GUI 테마 설정
ctk.set_appearance_mode("System")  # 시스템 테마 따라가기 (다크모드/라이트모드)
ctk.set_default_color_theme("blue")  # 파란색 강조 색상

class App(ctk.CTk):
    """
    [메인 애플리케이션 클래스] GUI 창과 시뮬레이션 로직을 모두 관리합니다.
    
    클래스를 사용하는 이유:
    - 관련된 데이터(변수)와 기능(함수)을 하나로 묶어 관리
    - 코드 재사용성과 유지보수성
    """
    def __init__(self):
        """
        [초기화 함수] 프로그램이 시작될 때 맨 처음 실행됩니다.
        GUI 구성요소를 만들고 시뮬레이션 상태를 초기화합니다.
        """
        super().__init__()  # 부모 클래스(ctk.CTk) 초기화,부모 위임

        # 1단계: 기본 창 설정
        self.title("SmartFanAI 자동 제어 시뮬레이터")
        self.geometry("500x400")  # 가로 500px, 세로 400px

        # 2단계: 시뮬레이션 상태를 저장할 변수들 초기화
        # 이 변수들은 0.1초 업데이트되며 실시간으로 변합니다
        self.current_temperature = 25.0  # 현재 시스템 온도 (처음엔 실온 25도)
        self.target_temperature = 25.0   # 사용자가 설정한 목표 온도
        self.fan_rpm = 400               # AI가 예측한 팬 속도 (초기값: 최소 속도)

        # 3단계: AI 모델 로드
        self.model = None  # 모델을 담을 변수
        self.load_model()  # 아래 정의된 load_model() 함수 호출

        # 4단계: GUI 레이아웃 구성 (격자 방식)
        self.grid_columnconfigure(0, weight=1)  #동작(크기 조정 규칙)을 설정, 첫 번째 열이 창 크기에 맞춰 늘어남

        # --- 제목 라벨 ---
        self.title_label = ctk.CTkLabel(
            self, 
            text="AI 자동 온도 제어", 
            font=("Malgun Gothic", 24, "bold")  # 맑은 고딕, 24pt, 굵게
        )
        # grid(): 격자 형태로 위젯 배치
        # row=0, column=0: 첫 번째 행, 첫 번째 열
        # columnspan=2: 2개 열을 차지 (넓게 배치)
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        # --- 목표 온도 설정 프레임 ---
        # Frame: 관련된 위젯들을 그룹으로 묶는 컨테이너
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        # sticky="ew": east(동쪽)와 west(서쪽)로 늘어남 = 가로로 꽉 참->예쁘게
        self.control_frame.grid_columnconfigure(1, weight=1)

        # 라벨: "목표 온도 (°C)" 안내문
        ctk.CTkLabel(
            self.control_frame, 
            text="목표 온도 (°C)", 
            font=("Malgun Gothic", 16)
        ).grid(row=0, column=0, padx=10, pady=10)
        
        # 입력창: 사용자가 숫자를 입력할 수 있는 텍스트 상자
        self.temp_entry = ctk.CTkEntry(
            self.control_frame, 
            placeholder_text="예: 75.0",  # 입력 전 보이는 안내 문구
            width=120
        )
        self.temp_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # 버튼: 클릭하면 set_target_temperature() 함수 실행
        self.set_button = ctk.CTkButton(
            self.control_frame, 
            text="설정", 
            command=self.set_target_temperature  # 함수 이름만 쓰기 (괄호 X)
        )
        self.set_button.grid(row=0, column=2, padx=10, pady=10)

        # --- 실시간 상태 표시 프레임 ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.status_frame.grid_columnconfigure(1, weight=1)

        # "현재 온도:" 고정 라벨
        ctk.CTkLabel(
            self.status_frame, 
            text="현재 온도:", 
            font=("Malgun Gothic", 18)
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # 현재 온도 값 표시 (크고 파란색으로 강조)
        self.current_temp_label = ctk.CTkLabel(
            self, 
            text=f"{self.current_temperature:.1f} °C",  # .1f: 소수점 1자리
            font=("Malgun Gothic", 48, "bold"), 
            text_color="#3399FF"  # 파란색
        )
        self.current_temp_label.grid(row=3, column=0, columnspan=2, pady=10)

        # "AI 예측 팬 속도:" 고정 라벨
        ctk.CTkLabel(
            self.status_frame, 
            text="AI 예측 팬 속도:", 
            font=("Malgun Gothic", 18)
        ).grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        # AI가 예측한 RPM 값 표시 (녹색으로 강조)
        self.rpm_label = ctk.CTkLabel(
            self, 
            text=f"{self.fan_rpm} RPM", 
            font=("Malgun Gothic", 32, "bold"), 
            text_color="#00C000"  # 녹색
        )
        self.rpm_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # 5단계: 시뮬레이션 루프 시작
        # 아래 정의된 update_simulation()을 0.1초마다 자동 실행
        self.update_simulation()

    def load_model(self):
        """
        [AI 모델 로드 함수] 저장된 AI 모델 파일을 불러옵니다.
        
        실행 시점: 프로그램 시작 직후 (초기화 중)
        """
        try:
            # joblib.load(): pkl 파일에서 파이썬 객체 복원
            self.model = joblib.load('models/basic_model.pkl')
            print("모델 로드 성공.")
            # 이제 self.model.predict()로 예측 가능!
        except FileNotFoundError:
            # 파일이 없으면 에러 팝업 표시
            messagebox.showerror(
                "모델 없음", 
                "학습된 모델(basic_model.pkl)이 없습니다.\n프로그램을 종료합니다."
            )
            # 0.1초 후 프로그램 종료
            self.after(100, self.destroy)

    def set_target_temperature(self):
        """
        [목표 온도 설정 함수] 사용자가 입력한 값을 목표 온도로 설정합니다.
        
        실행 시점: 사용자가 "설정" 버튼을 클릭할 때
        
        과정:
        1. 텍스트 입력창에서 값 읽기
        2. 숫자로 변환 (문자열 → 실수)
        3. 유효성 검사 (0~100도 범위)
        4. 목표 온도 변수 업데이트
        """
        try:
            # 입력창(Entry)에서 텍스트 가져오기
            # 예: "75.5" (문자열)
            target = float(self.temp_entry.get())  # 문자열 → 실수 변환
            
            # 유효성 검사: 물리적으로 가능한 온도 범위
            if 0 <= target <= 100:
                self.target_temperature = target
                print(f"목표 온도가 {self.target_temperature}°C로 설정되었습니다.")
                # 콘솔 출력 예시: "목표 온도가 75.5°C로 설정되었습니다."
            else:
                # 범위를 벗어난 경우 경고 팝업
                messagebox.showwarning(
                    "입력 오류", 
                    "온도는 0에서 100 사이의 숫자로 입력해주세요."
                )
        except (ValueError, TypeError):
            # 숫자가 아닌 값을 입력한 경우 (예: "abc", 빈 문자열)
            messagebox.showwarning(
                "입력 오류", 
                "유효한 숫자를 입력해주세요."
            )

    def update_simulation(self):
        """
        [핵심 시뮬레이션 함수] 0.1초마다 실행되며 다음 작업을 수행합니다:
        1. 현재 온도를 목표 온도에 가깝게 조금씩 변경 (열역학적 시간 지연 모사)
        2. AI가 현재 온도를 보고 적절한 팬 RPM 예측
        3. 화면에 표시된 값들 업데이트
        4. 0.1초 후 자기 자신을 다시 호출 (무한 루프)
        
        이 함수 존나 중요
        """
        
        # ===== 1단계: 온도 시뮬레이션 (열역학 법칙 적용) =====
        # 실제 냉각 시스템은 목표 온도에 '즉시' 도달 X
        # 열용량, 열전도율 등으로 인해 '서서히' 변화
        
        # 온도 차이가 0.1도 미만이면 목표에 도달한 것으로 간주
        if abs(self.target_temperature - self.current_temperature) < 0.1:
            self.current_temperature = self.target_temperature
            
        # 목표가 현재보다 높으면 온도 상승 (열 발생 증가 상황)
        elif self.target_temperature > self.current_temperature:
            self.current_temperature += 0.2  # 0.1초당 0.2도씩 상승
            # 예: 25도 → 25.2도 → 25.4도 → ... → 75도
            
        # 목표가 현재보다 낮으면 온도 하강 (냉각 진행 상황)
        elif self.target_temperature < self.current_temperature:
            self.current_temperature -= 0.2  # 0.1초당 0.2도씩 하강
            # 예: 75도 → 74.8도 → 74.6도 → ... → 25도
            
        # 왜 0.2도씩? 
        # - 너무 빠르면 비현실적 
        # - 너무 느리면 지루
        # - 0.2도는 적절한 값

        # ===== 2단계: AI 예측 (핵심 머신러닝 부분) =====
        if self.model:
            # 현재 온도를 AI가 이해할 수 있는 형태로 변환
            # numpy 배열, 2차원 형태 [[온도값]]로 만들어야 함
            temp_array = np.array([[self.current_temperature]])
            #입력 객체(리스트·튜플 등)를 NumPy의 n차원 배열로 변환하는 기본 생성 함수
            # 예시: current_temperature가 52.3이면
            # temp_array = [[52.3]] 형태가 됨
            
            # 왜 2차원 배열? 
            # - AI는 여러 샘플을 한 번에 처리
            # - 한 개만 예측해도 [[값]] 형태
            #   한 장이어도 봉투에 넣어서 내는 것과 비슷
            
            # AI 모델에게 예측 요청!
            # "52.3도일 때 팬을 몇 RPM으로 돌려야 할까?"
            predicted_rpm = self.model.predict(temp_array)[0]
            # predict()는 배열을 반환하므로 [0]으로 첫 번째 값만 추출
            # 예측 결과 예시: predicted_rpm = 2754.8
            
            # ===== 현실성 확보: 음수 RPM 방지 =====
            # AI가 가끔 이상한 값을 예측할 수 있음 (특히 극단적 온도에서)
            # 물리적으로 팬 속도는 0 미만일 수 없으므로 보정
            self.fan_rpm = max(0, int(predicted_rpm))
            # max(0, ...): 0과 predicted_rpm 중 큰 값 선택
            # int(...): 소수점 제거 (RPM은 정수로 표시)
            # 예: -50 → 0, 2754.8 → 2754

        # ===== 3단계: 화면의 모든 정보 업데이트 =====
        self.update_display()  # 아래 정의된 함수 호출

        # ===== 4단계: 0.1초 후 이 함수를 다시 실행 (재귀 호출) =====
        # after(밀리초, 함수): 일정 시간 후 함수 실행
        # 100 밀리초 = 0.1초
        self.after(100, self.update_simulation)
        # update_simulation() 무한 반복
        # → 실시간 시뮬레이션 효과
        
        # 예: 0초 → 0.1초 → 0.2초 → 0.3초 → ...
        #     각 시점마다 온도 업데이트, AI 예측, 화면 갱신

    def update_display(self):
        """
        [화면 갱신 함수] 현재 상태를 GUI에 반영합니다.
        
        실행 시점: update_simulation()에서 매 0.1초마다 호출됨
        
        작업:
        1. 온도 라벨 텍스트 업데이트
        2. RPM 라벨 텍스트 업데이트
        3. 온도에 따라 라벨 색상 변경 (시각적 피드백)
        """
        
        # 1단계: 현재 온도 표시 업데이트
        self.current_temp_label.configure(
            text=f"{self.current_temperature:.1f} °C"
        )
        #configure는 CTk 기반 커스텀 위젯의 속성들을 한 번에 업데이트하는 메서드
        # .1f: 소수점 1자리까지 표시
        # 예: 52.345 → "52.3 °C"
        
        # 2단계: AI 예측 RPM 표시 업데이트
        self.rpm_label.configure(
            text=f"{self.fan_rpm} RPM"
        )
        # 예: 2754 → "2754 RPM"

        # 3단계: 온도에 따른 색상 변경 (위험도 표시)
        # 열역학적 관점: 온도가 높을수록 위험하므로 색상으로 경고
        temp_color = "#3399FF"  # 기본: 파란색 (안전)
        
        if self.current_temperature > 75:
            temp_color = "#FF3333"  # 빨간색 (위험! CPU 손상 위험 구간)
            # 75도 초과: 대부분의 CPU 안전 온도 초과
        elif self.current_temperature > 55:
            temp_color = "#FF9933"  # 주황색 (경고! 주의 필요)
            # 55~75도: 고부하 상태, 지속되면 위험
        # else: 55도 이하는 파란색 유지 (정상 작동 온도)
        
        # 색상 적용
        self.current_temp_label.configure(text_color=temp_color)
        
        # 시각적 효과:
        # 25도 → 파란색 (안심)
        # 60도 → 주황색 (조심)
        # 80도 → 빨간색 (위험!)
        # 사용자가 한눈에 상황을 파악

# ===== 프로그램 시작점 =====
if __name__ == "__main__":
    
    # 시작 전 모델 파일 존재 여부 확인
    if not os.path.exists('models/basic_model.pkl'):
        # 모델이 없으면 안내 팝업 표시
        messagebox.showinfo(
            "준비", 
            "모델 파일이 없습니다. model_trainer.py를 먼저 실행하여 모델을 생성해주세요."
        )
    
    # GUI 애플리케이션 실행
    # 1. App 클래스의 인스턴스(객체) 생성
    #    → __init__() 자동 실행 → GUI 구성
    app = App()
    
    # 2. 이벤트 루프 시작
    #    → 사용자의 클릭, 키보드 입력 등을 계속 감지
    #    → update_simulation()이 0.1초마다 자동 실행
    #    → 창을 닫을 때까지 프로그램 유지
    app.mainloop()