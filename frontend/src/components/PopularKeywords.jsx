// src/components/PopularKeywords.jsx
import { useEffect, useState } from "react";

console.log("API_URL =", process.env.REACT_APP_API_URL);

export default function PopularKeywords({ onSelect }) {
  const [keys, setKeys] = useState([]);

  useEffect(() => {
  fetch("http://localhost:8000/popular_keywords/")
    .then(r => r.json())
    .then(setKeys)
    .catch(e => console.error("인기 키워드 불러오기 실패:", e));
}, []);

  if (!keys.length) return null;

  return (
    <div className="popular-keywords">
      <h3>🔥 오늘의 인기 뉴스 키워드</h3>
      <div className="keyword-list">
        {keys.map(({ keyword, news_count }) => (
          <button
            key={keyword}
            className="keyword-chip"
            onClick={() => onSelect(keyword)}
          >
            {keyword} ({news_count})
          </button>
        ))}
      </div>
    </div>
  );
}
