# 🤖 AI 뉴스 브리핑 챗봇

**"오늘 가장 중요한 뉴스, AI가 찾아드립니다."**

사용자의 모호한 질문 속 숨은 의도를 파악하여, 가장 관련성 높은 최신 뉴스를 찾아 분석하고 요약해주는 지능형 뉴스 챗봇 프로젝트입니다.

---

## 🌟 주요 기능 (Key Features)

### 1. 지능형 이중 쿼리 (Intelligent Double-Query)
- 사용자의 모호한 초기 질문(예: "요즘 물가 왜 이래?")을 바탕으로 1차 뉴스 검색을 수행합니다.
- 1차 검색 결과를 **LLM(GPT-4o)이 분석**하여, 사용자의 진짜 의도를 담은 **핵심적인 2차 검색어를 자동으로 생성**합니다. (예: "소비자물가지수 동향 및 농산물 가격 급등 원인")
- 정제된 2차 검색어로 다시 뉴스를 찾아, 훨씬 더 정확하고 깊이 있는 분석 결과를 제공합니다.

### 2. LLM 기반 하이브리드 본문 추출
- 어떤 언론사 사이트를 만나더라도 안정적으로 본문을 추출하기 위해 **하이브리드(Hybrid) 방식을 사용**합니다.
- **(1단계)** `BeautifulSoup`으로 네이버 뉴스와 같이 자주 방문하는 사이트의 본문을 빠르게 찾아냅니다.
- **(2단계)** 처음 보는 구조의 사이트에서는 불필요한 HTML 태그(`<script>`, `<header>` 등)를 먼저 제거하여 AI의 작업 부담을 줄여줍니다.
- **(3단계)** 1, 2단계에서 정제된 HTML 조각을 **LLM(`extraction_chain`)**에게 전달하여, 최종적으로 광고나 관련 뉴스 등을 모두 걸러낸 순수한 기사 본문만 정확하게 추출합니다.

### 3. 음성 인터페이스 (Voice Interface)
- **STT (Speech-to-Text):** 마이크 버튼을 통해 음성으로 질문하고 뉴스를 검색할 수 있습니다. (OpenAI `whisper-1` 모델 사용)
- **TTS (Text-to-Speech):** AI가 분석한 최종 트렌드 요약은 자연스러운 음성으로 브리핑 받을 수 있습니다. (OpenAI `tts-1` 모델 사용)

### 4. 동시성 제어 및 오류 처리
- 다수의 뉴스 기사를 동시에 크롤링하고 AI에게 분석을 요청할 때 발생할 수 있는 **API 과부하(`RateLimitError`) 문제**를 `asyncio.Semaphore`를 이용해 동시 요청 수를 제어하여 안정적으로 해결했습니다.
- 보안이 취약한 오래된 웹사이트 접속 시 발생하는 **SSL 오류** 등 다양한 네트워크 예외 상황을 처리하여 프로그램의 안정성을 높였습니다.

---

## 🛠️ 기술 스택 (Tech Stack)

| 구분 | 기술 |
| :--- | :--- |
| **Backend** | `Python`, `FastAPI`, `LangChain`, `OpenAI API (GPT-4o)`, `httpx`, `BeautifulSoup` |
| **Frontend** | `React.js`, `JavaScript (ES6+)`, `CSS` |
| **APIs** | `Naver News Search API`, `OpenAI API (STT/TTS)` |
| **Infra** | `uvicorn` |

---

## ⚙️ 시작하기 (Getting Started)

### 1. 프로젝트 복제

```bash
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name
```

### 2. 백엔드 설정

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필요 라이브러리 설치
pip install -r requirements.txt
```

### 3. 프론트엔드 설정

```bash
# 프론트엔드 디렉토리로 이동
cd ../frontend

# 필요 라이브러리 설치
npm install
```

### 4. 환경변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 아래와 같이 API 키를 입력해주세요.

```.env
# .env

# OpenAI API 키
OPENAI_API_KEY="sk-..."

# Naver Developers API 키
NAVER_CLIENT_ID="..."
NAVER_CLIENT_SECRET="..."
```

---

## ▶️ 실행하기 (How to Run)

### 1. 백엔드 서버 실행

백엔드 디렉토리(`backend`)에서 아래 명령어를 실행하세요.

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 프론트엔드 서버 실행

프론트엔드 디렉토리(`frontend`)에서 아래 명령어를 실행하세요.

```bash
npm start
```

이제 브라우저에서 `http://localhost:3000`으로 접속하여 AI 뉴스 브리핑 챗봇을 사용할 수 있습니다!

---

## 💭 프로젝트 후기

비전공자로서 AI 개발자의 길을 걸으며, 복잡한 문제를 정의하고 기술적으로 해결해나가는 과정을 깊이 있게 경험할 수 있었던 프로젝트입니다. 특히, 단순히 API를 호출하는 것을 넘어 **LLM의 동작 방식을 이해하고, 여러 AI 에이전트가 협업하는 파이프라인을 직접 설계**하며 한 단계 더 성장할 수 있었습니다. 사용자의 모호한 질문에서 핵심을 꿰뚫는 '이중 쿼리' 시스템과, 어떤 웹 환경에서도 안정적으로 정보를 추출하는 '하이브리드 본문 추출' 로직은 이 프로젝트의 가장 큰 자랑거리입니다. 앞으로도 기술의 본질을 탐구하며, 사람들에게 실질적인 가치를 제공하는 개발자로 성장해나가겠습니다.
