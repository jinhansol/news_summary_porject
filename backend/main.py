import os
from io import BytesIO
import requests
import tempfile
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging

from voice_chat import generate_audio_file
from patched_cleanre import clean_text
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# --- 로깅 설정 (디버그 로그는 INFO 레벨 이상만 출력) ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# --- 환경 변수 로드 ---
load_dotenv()
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
if not (OPENAI_API_KEY and NAVER_CLIENT_ID and NAVER_CLIENT_SECRET):
    raise ValueError("OPENAI_API_KEY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 모두 .env에 정의되어 있어야 합니다.")

# --- OpenAI 클라이언트 (STT/TTS) ---
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# --- FastAPI 앱 설정 ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")

# --- Pydantic 모델 ---
class NewsTrendRequest(BaseModel):
    keyword: str

class TTSRequest(BaseModel):
    text: str

# --- 키워드 → 요약 목적 매핑 ---
def map_keyword_to_purpose(keyword: str) -> str:
    KEYWORD_PURPOSE_MAP = {
        "코인": "가상자산 뉴스 요약", "비트코인": "가상자산 뉴스 요약", "이더리움": "가상자산 뉴스 요약",
        "주식": "주식 시장 트렌드 요약", "ETF": "금융 투자 요약", "테슬라": "글로벌 기업 뉴스 요약",
        "애플": "IT 기업 트렌드 요약", "취업": "취업 시장 동향 요약", "부동산": "부동산 뉴스 요약",
        "아파트": "주택 시장 뉴스 요약", "AI": "인공지능 트렌드 요약", "챗GPT": "최신 AI 뉴스 요약",
        "메타버스": "신기술 트렌드 요약"
    }
    for k, p in KEYWORD_PURPOSE_MAP.items():
        if k in keyword:
            return p
    return f"{keyword} 관련 뉴스 요약"

# --- LangChain LLM 설정 ---
llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)
summary_chain = (
    PromptTemplate.from_template(
        "너는 한국어 뉴스 기사를 요약하는 AI야.\n"
        "요약 목적: {purpose}\n"
        "뉴스 기사 원문: {article}"
    ) | llm
)
trend_chain = (
    PromptTemplate.from_template(
        "다음은 기사 요약들입니다.\n"
        "'{purpose}'에 대한 최신 트렌드를 3~5줄로 설명해줘.\n"
        "요약들:\n{summaries}"
    ) | llm
)

# --- 네이버 뉴스검색 Open API 래퍼 ---
def search_naver_news(keyword: str, max_articles: int = 3):
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": keyword, "display": max_articles, "start": 1, "sort": "date"}
    res = requests.get(url, headers=headers, params=params, timeout=5)
    res.raise_for_status()
    items = res.json().get("items", [])
    if not items:
        raise HTTPException(status_code=404, detail="관련 뉴스 기사를 찾을 수 없습니다.")
    return [{"title": it["title"], "url": it["link"]} for it in items]

# --- 기사 본문 추출 ---
def extract_article_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=5)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, "html.parser")
    node = soup.select_one(
        "div#articleBodyContents, article#dic_area, div#dic_area, div.article_body"
    )
    if node:
        for bad in node.select("script, .ad_banner, .advertisement"):
            bad.decompose()
        return node.get_text(separator=" ", strip=True)
    paras = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 50]
    if paras:
        return "\n".join(paras)
    raise HTTPException(status_code=500, detail=f"본문 추출 실패: {url}")

# --- API 엔드포인트 ---
@app.post("/news_trend/")
def news_trend(req: NewsTrendRequest):
    purpose = map_keyword_to_purpose(req.keyword)
    links = search_naver_news(req.keyword, max_articles=3)

    summaries = []
    details = []
    for link in links:
        art = extract_article_text(link["url"])
        clean = clean_text(art, "KR")
        summ = summary_chain.invoke({"purpose": purpose, "article": clean}).content
        summaries.append(summ)
        details.append({"title": link["title"], "url": link["url"], "summary": summ})

    trend = trend_chain.invoke({"purpose": purpose, "summaries": "\n".join(summaries)}).content
    return {
        "keyword": req.keyword,
        "purpose": purpose,
        "trend_digest": trend,
        "trend_articles": details
    }

@app.get("/popular_keywords")
@app.get("/popular_keywords/")
def popular_keywords():
    return [
        {"keyword": "코인", "news_count": 120},
        {"keyword": "부동산", "news_count": 95},
        {"keyword": "아파트", "news_count": 80},
        {"keyword": "AI", "news_count": 60},
        {"keyword": "테슬라", "news_count": 35},
    ]

@app.post("/generate-tts/")
async def generate_tts(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="TTS 텍스트가 없습니다.")
    path = generate_audio_file(req.text)
    if not path:
        raise HTTPException(status_code=500, detail="음성 파일 생성 실패")
    return FileResponse(path=path, media_type="audio/mpeg", filename="response.mp3")

from io import BytesIO

@app.post("/generate-stt/")
async def generate_stt(file: UploadFile = File(...)):
    data = await file.read()
    # BytesIO로 감싸고 .name에 원본 filename을 지정
    audio_stream = BytesIO(data)
    audio_stream.name = file.filename   # ex) "rec.webm"
    audio_stream.seek(0)

    try:
        transcription = openai_client.audio.transcriptions.create(
            file=audio_stream,
            model="whisper-1"
        )
        return {"text": transcription.text}

    except Exception:
        logger.exception("🎤 STT 처리 중 예외 발생")
        raise HTTPException(500, "STT 처리 중 서버 오류가 발생했습니다.")



@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("../frontend/build/index.html")
