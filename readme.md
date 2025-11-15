#학습 데이터 생성:
(CMD 창에 (venv)가 활성화된 상태인지 확인하세요.)
python data_simulator.py

#AI 모델 훈련:
python model_trainer.py

#실행
(CMD 창에 (venv)가 활성화된 상태인지 확인하세요.)
python main_gui.py

===============================================

각 라이브러리의 역할
customtkinter: 현대적인 GUI(사용자 인터페이스)를 만듭니다.
scikit-learn: AI 모델(선형 회귀, 랜덤 포레스트)을 만들고 훈련시킵니다.
pandas: CSV 데이터를 읽고 관리하는 데 사용됩니다.
numpy: 효율적인 숫자 계산 및 데이터 배열 처리를 담당합니다.
joblib: 훈련된 AI 모델을 파일(.pkl)로 저장하고 불러오는 데 사용됩니다.