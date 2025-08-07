import React, { useState } from "react";

export default function SearchBar({ onSearch, onRecordingStart, onRecordingEnd }) {
  const [text, setText] = useState("");

  // 텍스트 검색은 그대로
  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(text);
    setText("");
  };

  // 🎤 버튼은 녹음 시작/종료만
  const handleSTT = () => {
    if (onRecordingStart) onRecordingStart();
    // 2초 뒤 자동으로 녹음 중지
    setTimeout(() => {
      if (onRecordingEnd) onRecordingEnd();
    }, 2000); // 원하는 녹음 길이만큼 조정
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="무엇이든 물어보세요"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button type="submit">검색</button>
      <button type="button" onClick={handleSTT}>🎤</button>
    </form>
  );
}
