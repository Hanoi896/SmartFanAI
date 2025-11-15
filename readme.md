1단계: 명령 프롬프트(CMD) 실행 및 폴더 이동
CMD 실행:
프로젝트 폴더로 이동:

2단계: 가상 환경 생성 및 라이브러리 설치 (최초 한 번만)
#이 단계는 프로젝트를 처음 설정할 때만 필요합니다.
가상 환경 생성:
CMD 창에 아래 명령어를 입력하여 venv가상 환경을 만듭니다.
python -m venv venv

가상 환경 활성화:
이제 생성된 가상 환경에 접속합니다.
.\venv\Scripts\activate
#window 기준

성공 -> (venv)
(venv) C:\Users\YourUsername\Desktop\SmartFanAI>

필요한 라이브러리 설치:
pip 이용 -> 라이브러리 설치
pip install customtkinter scikit-learn pandas numpy joblib matplotlib

3단계: AI 모델 사전 훈련
데이터와 AI 모델을 생성합니다.

학습 데이터 생성:
(CMD 창에 (venv)가 활성화 상태 확인)
python data_simulator.py

AI 모델 훈련:
python model_trainer.py

4단계: 프로그램 실행
메인 프로그램을 실행해 시작
(CMD 창에 (venv)가 활성화 상태 확인)
python main_gui.py

잠시 후 GUI 창

==============================================================================================================================

각 라이브러리의 역할
customtkinter: 현대적인 GUI(사용자 인터페이스)를 만듭니다.
scikit-learn: AI 모델(선형 회귀, 랜덤 포레스트)을 만들고 훈련시킵니다.
pandas: CSV 데이터를 읽고 관리하는 데 사용됩니다.
numpy: 효율적인 숫자 계산 및 데이터 배열 처리를 담당합니다.
joblib: 훈련된 AI 모델을 파일(.pkl)로 저장하고 불러오는 데 사용됩니다.

==============================================================================================================================

SmartFanAI_Simple/
│
├── venv/                   # 파이썬 가상 환경 폴더
│
├── data/                   # 데이터 저장 폴더
│   └── simulated_fan_data.csv  # data_simulator.py 실행 후 생성
│
├── models/                 # 훈련된 AI 모델 저장 폴더
│   └── basic_model.pkl       # model_trainer.py 실행 후 생성
│
├── data_simulator.py       # AI 학습에 필요한 가상 데이터를 생성
│
├── model_trainer.py        # 기본 선형 회귀 AI 모델을 훈련
│
└── main_gui.py             # 메인 프로그램-자동 제어 GUI
