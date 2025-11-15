# 파일명: data_simulator.py
# 목적: AI가 학습할 '온도-팬속도' 데이터를 인공적으로 생성하는 프로그램
# 비유: 실제 PC에서 센서 데이터를 모으는 대신, 가상으로 '교과서'를 만드는 과정

import pandas as pd
import numpy as np
import os

def get_rpm_from_temp(temp):
    """
    [핵심 함수] 온도에 따라 적절한 팬 속도(RPM)를 계산합니다.
    
    열역학 원리: 온도가 높을수록 더 많은 열을 방출해야 하므로 팬 속도를 높여야 합니다.
    
    온도 구간별 RPM 설정 근거:
    - 20도 이하: 400 RPM (저속, 아이들 상태 - 웹서핑, 문서작업)
    - 20~40도: 400 → 2000 RPM으로 선형 증가 (중간 부하 - 동영상 시청)
    - 40~60도: 2000 → 3600 RPM으로 선형 증가 (고부하 - 게임, 렌더링)
    - 60도 초과: 3600 RPM 고정 (최대 냉각 - 열평형 유지 필수)
    
    예시: 
    - 온도 25도 → 약 800 RPM (조용한 사무실 환경)
    - 온도 50도 → 약 2800 RPM (게임 중)
    - 온도 70도 → 3600 RPM (최대 냉각)
    """
    if temp <= 20:
        # 매우 낮은 온도: 최소 팬 속도로도 충분
        return 400
    elif 20 < temp <= 40:
        # 중간 온도 구간: 선형 보간으로 부드러운 증가
        # 공식: 시작값 + (현재온도 - 시작온도) * (증가폭 / 온도범위)
        return 400 + (temp - 20) * (2000 - 400) / (40 - 20)
    elif 40 < temp <= 60:
        # 고온 구간: 더 빠른 속도로 RPM 증가 (열 발생량이 급증)
        return 2000 + (temp - 40) * (3600 - 2000) / (60 - 40)
    else:
        # 위험 온도: 최대 속도로 강제 냉각
        return 3600

def generate_simulated_data(num_samples=2000):
    """
    [데이터 생성 함수] 실제 PC 환경을 모방한 2000개의 가상 데이터를 만듭니다.
    
    왜 2000개인가? 
    - AI 학습에는 충분히 많은 데이터가 필요합니다.
    - 너무 적으면 과소적합(underfitting), 너무 많으면 학습 시간 증가
    - 2000개는 학습과 효율의 균형점
    
    데이터 분포 전략:
    - 40%는 저부하(평균 25도) - 일상적인 사용 상황
    - 40%는 중부하(평균 45도) - 멀티태스킹, 게임
    - 20%는 고부하(평균 65도) - 렌더링, 압축 작업
    
    이렇게 나눈 이유: 실제 PC 사용 시간 중 대부분은 저~중부하 상태이므로
    """
    np.random.seed(42)  # 난수 고정: 매번 실행해도 같은 데이터 생성 (재현성 확보)
    
    # 1단계: 세 가지 부하 상황의 온도 데이터 생성
    temperatures = np.concatenate([
        # 저부하: 평균 25도, 표준편차 3도 (±3도 범위에서 변동)
        # 예: 23도, 26도, 27도 등으로 자연스럽게 분포
        np.random.normal(25, 3, int(num_samples * 0.4)),
        
        # 중부하: 평균 45도, 표준편차 5도 (변동폭이 더 큼)
        # 이유: 중간 부하는 작업 종류가 다양해서 온도 변화도 크다
        np.random.normal(45, 5, int(num_samples * 0.4)),
        
        # 고부하: 평균 65도, 표준편차 4도
        np.random.normal(65, 4, int(num_samples * 0.2)),
    ])
    
    # 2단계: 데이터를 무작위로 섞기
    # 이유: AI가 순서에 영향받지 않고 순수하게 '온도-RPM 관계'만 학습하도록
    np.random.shuffle(temperatures)

    # 3단계: 각 온도에 대해 '온도-RPM' 쌍을 생성
    data = []
    for temp in temperatures:
        # 이론적인 RPM 계산 (위의 get_rpm_from_temp 함수 사용)
        base_rpm = get_rpm_from_temp(temp)
        
        # 4단계: 현실감을 위한 노이즈(잡음) 추가
        # 실제 센서는 완벽하지 않아 약간의 오차가 있음
        temp_with_noise = temp + np.random.normal(0, 0.5)  # ±0.5도 오차
        rpm_with_noise = base_rpm + np.random.normal(0, 50)  # ±50 RPM 오차
        
        # 예시: 이론상 50도 → 2800 RPM이지만
        # 실제 측정값은 49.7도 → 2830 RPM처럼 약간 다를 수 있음
        
        # 5단계: 데이터를 딕셔너리 형태로 저장
        data.append({
            'temperature': round(temp_with_noise, 2),  # 소수점 2자리로 반올림
            'fan_rpm': int(rpm_with_noise)  # 정수로 변환 (RPM은 정수값)
        })
        
    # 6단계: 리스트를 pandas DataFrame으로 변환
    # DataFrame은 엑셀처럼 표 형태로 데이터를 다루기 쉽게 해줌
    return pd.DataFrame(data)

def run_simulation():
    """
    [메인 실행 함수] 데이터 생성부터 파일 저장까지 전체 과정을 관리합니다.
    
    실행 순서:
    1. 'data' 폴더가 없으면 생성
    2. 2000개의 시뮬레이션 데이터 생성
    3. CSV 파일로 저장 (엑셀에서도 열 수 있는 범용 형식)
    """
    # 1단계: 저장할 폴더 확인 및 생성
    if not os.path.exists('data'):
        os.makedirs('data')  # 'data' 폴더가 없으면 자동 생성

    # 2단계: 시뮬레이션 데이터 생성
    simulated_df = generate_simulated_data(num_samples=2000)
    
    # 3단계: CSV 파일로 저장
    file_path = 'data/simulated_fan_data.csv'
    simulated_df.to_csv(file_path, index=False)  # index=False: 행 번호는 저장 안 함
    
    # 저장 완료 메시지
    print(f"{len(simulated_df)}개의 샘플 데이터가 생성되어 '{file_path}'에 저장되었습니다.")
    # 출력 예시: "2000개의 샘플 데이터가 생성되어 'data/simulated_fan_data.csv'에 저장되었습니다."

# 프로그램 시작점
if __name__ == '__main__':
    # 이 파일을 직접 실행했을 때만 run_simulation() 함수 실행
    # 다른 파일에서 import 했을 때는 실행되지 않음
    run_simulation()