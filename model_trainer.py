# 파일명: model_trainer.py 
# 목적: 생성된 데이터로 AI 모델을 학습시키고 저장하는 프로그램
# 비유: 학생(AI)에게 교과서(CSV 데이터)를 주고 공부시킨 후, 시험(테스트)을 보는 과정

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import joblib
import os

def train_basic_model():
    """
    [AI 학습 메인 함수] 선형 회귀 모델을 학습하고 평가하여 저장합니다.
    
    전체 흐름:
    1. CSV 데이터 불러오기
    2. 데이터를 훈련용/테스트용으로 분리
    3. AI 모델 학습
    4. 모델 성능 평가
    5. 학습된 모델 파일로 저장
    """
    data_path = 'data/simulated_fan_data.csv'
    
    # 1단계: 데이터 파일 읽기 (에러 처리 포함)
    try:
        df = pd.read_csv(data_path)
        # df는 DataFrame: 엑셀처럼 행(row)과 열(column)로 구성된 표
        # 예시 모습:
        #    temperature  fan_rpm
        # 0         25.3      850
        # 1         49.8     2750
        # 2         67.2     3580
    except FileNotFoundError:
        # 파일이 없을 경우 친절한 안내 메시지
        print(f"데이터 파일('{data_path}')을 찾을 수 없습니다.")
        print("먼저 data_simulator.py를 실행하여 데이터를 생성해주세요.")
        return  # 함수 종료

    # 2단계: 데이터를 입력(X)과 출력(y)로 분리
    # X: AI가 보고 판단할 정보 (온도)
    # y: AI가 예측해야 할 답 (팬 RPM)
    X = df[['temperature']]  # [[ ]]로 감싸야 DataFrame 형태 유지
    y = df['fan_rpm']        # [ ]만 쓰면 Series(라이브러리의 1차원 레이블 배열) 형태
    
    # 예시:
    # X:              y:
    # temperature    fan_rpm
    #    25.3    →    850
    #    49.8    →   2750
    #    67.2    →   3580

    # 3단계: 데이터를 훈련용 80% + 테스트용 20%로 분리
    # 왜 분리?
    # - 훈련용: AI가 '공부'하는 데이터
    # - 테스트용: AI가 처음 보는 데이터 '평가'
    # 비유: 수학 문제집 100문제 중 80문제로 공부, 20문제 시험
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2,      # 20%를 테스트용으로
        random_state=42     # 난수 고정 (재현성)
    )
    
    # 분리 결과:
    # X_train: 1600개 (80%) - AI 학습용 온도 데이터
    # y_train: 1600개 (80%) - AI 학습용 RPM 정답
    # X_test:   400개 (20%) - AI 평가용 온도 데이터
    # y_test:   400개 (20%) - AI 평가용 RPM 정답

    # 4단계: AI 모델 생성 및 학습
    print("기본 모델(선형 회귀) 학습을 시작합니다...")
    
    # LinearRegression: 가장 기본적인 AI 모델,scikit-learn의 선형 회귀 모델
    # 원리: y = ax + b 형태
    # 이 프로젝트에서는 'RPM = a * 온도 + b' 관계
    model = LinearRegression()
    
    # fit(): AI에게 데이터를 주고 '공부'시키는 과정
    # 최적의 a, b 값 계산
    model.fit(X_train, y_train)
    # 학습 후: model은 이제 온도를 입력받으면 RPM을 예측
    
    print("모델 학습 완료.")

    # 5단계: 학습된 모델의 성능 평가
    # 테스트 데이터로 예측 수행
    predictions = model.predict(X_test)
    # predictions: AI가 예측한 RPM 값들
    # 예시: [848, 2735, 3590, ...]
    
    # R2 Score(결정계수)로 성능 측정
    # R2 Score 의미:
    # - 1.0에 가까울수록 완벽한 예측 (100점)
    # - 0.5 정도면 보통 (50점)
    # - 0.0 이하면 무작위보다 못함 (0점 이하)
    score = r2_score(y_test, predictions)
    print(f"모델 성능(R2 Score): {score:.4f}")
    # 출력 예시: "모델 성능(R2 Score): 0.9856"
    # → 98.56%의 정확도! 매우 우수한 성능

    # 6단계: 학습된 모델을 파일로 저장
    # 왜 저장하는가?
    # - 매번 프로그램 실행할 때마다 학습하면 시간 낭비
    # - 한 번 학습한 '똑똑한 AI'를 파일로 저장해서 재사용
    if not os.path.exists('models'):
        os.makedirs('models')  # 'models' 폴더 생성
    
    model_path = 'models/basic_model.pkl'
    # joblib.dump(): 파이썬 객체를 파일로 저장,joblib 라이브러리 함수,파이썬 객체 디스크에 직렬화하여 저장
    # pkl 확장자: pickle 파일 (파이썬 전용 저장 형식)
    joblib.dump(model, model_path)
    
    print(f"학습된 모델이 '{model_path}'에 저장되었습니다.")
    # 이제 main_gui.py에서 이 파일을 불러와 바로 사용 가능

# 프로그램 시작점
if __name__ == '__main__':
    train_basic_model()