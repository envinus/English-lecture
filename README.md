# 📚 어린이 영어 학습 프로그램

9살 한국 어린이를 위한 자기주도 영어 학습 Streamlit 애플리케이션입니다.
StoryWeaver(storyweaver.org.in)의 동화책을 활용하여 재미있게 영어를 배울 수 있습니다.

## ✨ 주요 기능

### 1. 📖 동화책 추가하기
세 가지 방법으로 동화책을 추가할 수 있습니다:

#### 📄 PDF 업로드 (추천!)
- StoryWeaver에서 다운로드한 PDF 파일을 업로드
- 자동으로 텍스트와 이미지를 추출
- 한국어로 자동 번역

#### ✍️ 수동 입력
- 브라우저에서 동화책을 보면서 텍스트를 복사하여 입력
- 페이지별로 입력 가능
- 자동 번역 지원

#### 🔽 URL 크롤링 (현재 차단됨)
- StoryWeaver가 외부 접근을 차단하여 현재 사용 불가

### 2. 📚 읽기 모드
- 동화책의 삽화와 영어 문장을 보며 학습합니다
- **듣기 기능**: 문장을 원어민 발음으로 들을 수 있습니다 (TTS)
- **한국어 번역**: 클릭 한 번으로 한국어 뜻을 확인할 수 있습니다
- 이전/다음 버튼으로 페이지를 넘길 수 있습니다

### 3. 🗣️ 말하기 연습
- 문장을 듣고 따라 말하는 연습을 합니다
- 마이크로 녹음하면 발음을 자동으로 평가합니다 (STT)
- 유사도에 따라 칭찬 메시지와 풍선 효과를 받습니다

### 4. 🎮 단어 퀴즈
- 동화책에서 단어를 뽑아 3지선다 퀴즈를 만듭니다
- 영어 단어를 보고 올바른 한국어 뜻을 고릅니다
- 점수를 기록하여 학습 성취도를 확인할 수 있습니다

## 🛠️ 설치 방법

### 1. Python 설치
- Python 3.9 이상이 필요합니다
- [Python 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드하세요

### 2. 필수 패키지 설치

#### Windows 사용자

```bash
# 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

#### macOS/Linux 사용자

```bash
# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. PyAudio 설치 (말하기 기능용)

PyAudio는 운영체제에 따라 별도 설치가 필요할 수 있습니다:

#### Windows
```bash
pip install pipwin
pipwin install pyaudio
```

또는 [여기](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)에서 whl 파일을 다운로드하여 설치:
```bash
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
```

#### macOS
```bash
brew install portaudio
pip install pyaudio
```

#### Linux
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

## 🚀 실행 방법

### 1. 애플리케이션 실행

```bash
streamlit run app.py
```

### 2. 브라우저에서 자동으로 열립니다
- 자동으로 열리지 않으면 브라우저에서 `http://localhost:8501`로 접속하세요

## 📖 사용 방법

### 동화책 추가하기

#### 방법 1: PDF 업로드 (가장 쉬운 방법!)

1. [StoryWeaver 웹사이트](https://storyweaver.org.in/)로 이동
2. 원하는 동화책 찾기 (Level 1 추천)
3. 동화책 페이지에서 **"Download"** 버튼 클릭
4. **PDF** 형식 선택하여 다운로드
5. 앱의 사이드바에서 **"📄 PDF로 동화책 추가하기"** 섹션 열기
6. 다운로드한 PDF 파일 선택
7. (선택사항) 동화책 제목 입력
8. **"🚀 PDF 처리하기"** 버튼 클릭
9. 자동으로 텍스트 추출 및 번역됩니다!

#### 방법 2: 수동 입력

1. [StoryWeaver 웹사이트](https://storyweaver.org.in/)에서 동화책 열기
2. 앱의 사이드바에서 **"✍️ 수동으로 동화책 만들기"** 섹션 열기
3. 제목과 페이지 수 입력
4. **"📄 페이지 입력 시작"** 클릭
5. StoryWeaver 페이지를 보면서 텍스트를 복사하여 입력
6. 각 페이지마다 **"➕ 페이지 추가"** 클릭
7. 자동으로 한국어 번역됩니다!

### 학습하기

1. 왼쪽 사이드바에서 **동화책을 선택**합니다
2. **학습 모드**를 선택합니다 (읽기/말하기/퀴즈)
3. 화면의 안내에 따라 학습을 진행합니다

#### 읽기 모드
- 🔊 **듣기**: 문장을 소리 내어 읽어줍니다
- 🇰🇷 **해석 보기**: 한국어 번역을 보여주거나 숨깁니다
- ⬅️➡️ **이전/다음**: 페이지를 넘깁니다

#### 말하기 모드
- 🔊 **듣기**: 먼저 문장을 듣습니다
- 🎤 **녹음하고 평가받기**: 마이크 버튼을 누르고 문장을 따라 말합니다
- 발음이 얼마나 정확한지 평가받습니다

#### 단어 퀴즈 모드
- 🎲 **새 문제 만들기**: 동화책에서 단어를 뽑아 퀴즈를 만듭니다
- 🔊 **단어 듣기**: 문제의 단어를 듣습니다
- 정답을 선택하면 바로 결과를 확인할 수 있습니다

## 📁 프로젝트 구조

```
english_program/
├── app.py              # 메인 Streamlit 애플리케이션
├── crawler.py          # StoryWeaver 크롤러 모듈
├── stories.json        # 동화책 데이터 저장 파일
├── requirements.txt    # 필수 패키지 목록
└── README.md          # 프로젝트 설명서
```

## 🔧 문제 해결

### 마이크가 작동하지 않을 때
- 브라우저 설정에서 마이크 권한을 허용했는지 확인하세요
- Windows의 경우 설정 > 개인 정보 > 마이크에서 앱 권한을 확인하세요

### 음성 인식이 안 될 때
- 조용한 환경에서 시도해보세요
- 마이크에 가까이 대고 또박또박 말해보세요
- 인터넷 연결을 확인하세요 (Google Speech Recognition API 사용)

### 동화책 크롤링이 실패할 때
- URL이 정확한지 확인하세요 (읽기 모드 URL이어야 합니다)
- StoryWeaver 웹사이트의 구조가 변경되었을 수 있습니다
- 인터넷 연결을 확인하세요

### 번역이 안 될 때
- 인터넷 연결을 확인하세요
- 너무 자주 요청하면 일시적으로 차단될 수 있습니다 (잠시 후 다시 시도)

## 🎯 학습 팁

1. **매일 조금씩**: 하루에 한 페이지씩 꾸준히 학습하세요
2. **반복 학습**: 같은 동화책을 여러 번 읽으면 더 효과적입니다
3. **소리 내어 읽기**: 말하기 연습을 적극 활용하세요
4. **재미있게**: 퀴즈로 게임처럼 즐기면서 배우세요

## 📝 기술 스택

- **UI Framework**: Streamlit
- **Web Scraping**: BeautifulSoup4, Requests
- **Translation**: googletrans
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Speech-to-Text**: SpeechRecognition
- **Data Storage**: JSON

## 🤝 기여하기

버그를 발견하거나 개선 아이디어가 있다면 언제든 이슈를 등록하거나 Pull Request를 보내주세요!

## 📄 라이선스

이 프로젝트는 교육 목적으로 자유롭게 사용할 수 있습니다.

## ⚠️ 주의사항

- 이 프로그램은 StoryWeaver의 공개 콘텐츠를 사용합니다
- 크롤링한 콘텐츠는 개인 학습 용도로만 사용하세요
- 상업적 용도로 사용하지 마세요
- StoryWeaver의 이용 약관을 준수하세요

## 🎉 즐거운 학습 되세요!

영어 공부를 재미있게 할 수 있기를 바랍니다. 화이팅! 💪
