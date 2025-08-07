// src/App.js
import { useState, useEffect, useRef } from "react";
import PopularKeywords from "./components/PopularKeywords";
import SearchBar from "./components/SearchBar";
import ChatBox from "./components/ChatBox";
import Loader from "./components/Loader";
import hamster from "./assets/hamster.png";
import hamster2 from "./assets/hamster2.png";
import hamster3 from "./assets/hamster3.png";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL;

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const recorderRef = useRef(null);
  const chunksRef   = useRef([]);

  // 대화 기록 로드/저장
  useEffect(() => {
    const saved = localStorage.getItem("chat-log");
    if (saved) setMessages(JSON.parse(saved));
  }, []);
  useEffect(() => {
    localStorage.setItem("chat-log", JSON.stringify(messages));
  }, [messages]);

  // 인기 키워드 선택
  const handleSelectKeyword = (keyword) => {
    handleSearch(keyword);
  };

  // 텍스트 → TTS
  const playAudio = async (text) => {
    if (!text?.trim()) return;
    const res = await fetch(`${API_URL}/generate-tts/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const blob = await res.blob();
    new Audio(URL.createObjectURL(blob)).play();
  };

  // 뉴스 검색 & 요약
  const handleSearch = async (query) => {
    if (!query?.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/news_trend/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword: query }),
      });
      if (!res.ok) throw new Error(res.status);
      const data = await res.json();
      playAudio(data.trend_digest);
      setMessages((prev) => [...prev, { query: data.keyword, results: data }]);
    } catch (e) {
      console.error("뉴스 요청 실패:", e);
      alert("뉴스 요약에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // STT 녹음 시작 / 중지
  const startRecording = async () => {
    setRecording(true);
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    recorderRef.current = recorder;
    chunksRef.current = [];
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = async () => {
  setRecording(false);
  const blob = new Blob(chunksRef.current, { type: "audio/webm" });
  const form = new FormData();
  form.append("file", blob, "rec.webm");
  console.log("STT 요청 URL:", `${API_URL}/generate-stt/`);

  try {
    // ① URL 확인: 반드시 정확히 매치 (/generate-stt/ 끝에 슬래시 포함 여부)
    const res = await fetch(`${API_URL}/generate-stt/`, {
      method: "POST",
      body: form,
    });

    // ② 네트워크 에러나 CORS 차단 시 fetch 자체가 throw 되니 여기서 잡힙니다.
    //    또한, HTTP 500 같은 응답이면 res.ok===false 이므로 다음 블록으로 갑니다.
    if (!res.ok) {
      const errBody = await res.json().catch(() => null);
      throw new Error(errBody?.detail || `STT HTTP 에러 ${res.status}`);
    }

    // ③ 정상 JSON 파싱
    const { text } = await res.json();
    handleSearch(text);

  } catch (err) {
    console.error("🎤 STT 요청 실패:", err);
    alert("음성 인식 요청이 실패했습니다.\n(네트워크, CORS 설정, 서버 로그를 확인해 주세요.)");
  }
};
    recorder.start();
  };
  const stopRecording = () => recorderRef.current?.stop();

  // 대화 기록 삭제
  const clearMessages = () => {
    setMessages([]);
    localStorage.removeItem("chat-log");
  };

  return (
    <div className="app">
      <main className="main-content">
        <div className="center-area">

          {/* ← 복구: 햄스터 영역 */}
          <div className="top-hamster-area">
            {recording ? null : (
              <>
                <img
                  src={loading ? hamster2 : hamster}
                  alt="hamster"
                  className="hamster-main"
                />
                {!loading && messages.length === 0 && (
                  <h2 className="prompt-text">“요즘 화제되는 뉴스, 같이 찾아볼까요? 🔍”</h2>
                )}
              </>
            )}
          </div>

          {/* 1) 인기 키워드 */}
          <PopularKeywords onSelect={handleSelectKeyword} />

          {/* 2) 검색바 */}
          <SearchBar
            onSearch={handleSearch}
            onRecordingStart={startRecording}
            onRecordingEnd={stopRecording}
          />

          {/* 3) 로딩 / 녹음 / 채팅박스 */}
          {recording ? (
            // 녹음 중엔 햄스터 로더
            <Loader image={hamster3} text="듣고 있어요" />
          ) : loading ? (
            // 뉴스 불러오는 중에는 텍스트만
            <div className="loading-only">
              뉴스 불러오는 중...
            </div>
          ) : (
            <ChatBox messages={messages} onClear={clearMessages} />
          )}

        </div>
      </main>
    </div>
  );
}

export default App;
