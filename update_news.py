
import feedparser
import datetime
import ssl
import socket

# 보안 연결(SSL) 에러 방지 설정
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 타임아웃 설정 (사이트 응답이 느릴 경우 대비)
socket.setdefaulttimeout(20)

# 뉴스 RSS 주소 (가장 안정적인 주소 위주)
RSS_FEEDS = {
    "전자신문": "https://www.etnews.com/section/main/rss",
    "디지털타임스": "http://www.dt.co.kr/rss/dt_all.xml",
    "인공지능신문": "https://www.aitimes.kr/rss/all.xml",
    "NYT(Tech)": "https://rss.nytimes.com/services/xml/rss/ntms/technology.xml",
    "IEEE": "https://spectrum.ieee.org/rss/blog/spectrometer/fulltext"
}

def get_latest_news():
    all_news = []
    # 브라우저인 것처럼 보이게 하는 설정 (매우 중요)
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    for media, url in RSS_FEEDS.items():
        try:
            # 에이전트 정보를 포함하여 피드 요청
            feed = feedparser.parse(url, agent=user_agent)
            
            if not feed.entries:
                print(f"{media}: 기사를 찾을 수 없습니다.")
                continue

            for entry in feed.entries[:3]: # 매체당 3개씩
                # 요약 내용 정제
                summary = entry.summary if 'summary' in entry else "상세 내용 요약은 기사 원문을 확인해 주세요."
                if '<' in summary: # HTML 태그 제거
                    import re
                    summary = re.sub('<[^<]+?>', '', summary)
                
                all_news.append({
                    "media": media,
                    "title": entry.title.strip(),
                    "desc": summary[:160].strip() + "..."
                })
        except Exception as e:
            print(f"{media} 수집 중 오류: {e}")
            continue
            
    return all_news

def update_html(news_data):
    # 만약 수집 실패 시 더미 데이터가 아닌 안내 문구 출력
    if not news_data:
        news_data = [{"media": "시스템", "title": "현재 뉴스 소스를 불러오는 중입니다.", "desc": "잠시 후 [Run Workflow]를 다시 실행해 주세요."}]
        
    today = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Tech Briefing</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {{ --primary-blue: #0d6efd; }}
        body {{ background: #f8fafc; font-family: 'Pretendard', sans-serif; word-break: keep-all; }}
        .header {{ text-align: center; padding: 60px 20px; background: #fff; border-bottom: 5px solid var(--primary-blue); margin-bottom: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
        .news-card {{ background: #fff; border-radius: 15px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 6px solid var(--primary-blue); height: 100%; transition: 0.3s; }}
        .news-card:hover {{ transform: translateY(-5px); }}
        .badge-media {{ background: #f1f5f9; color: #334155; font-weight: 700; padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; border: 1px solid #e2e8f0; }}
        .designer {{ font-size: 1.1rem; color: var(--primary-blue); font-weight: 600; margin-bottom: 15px; letter-spacing: 0.5px; }}
        @media (min-width: 992px) {{ .news-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; }} }}
    </style>
</head>
<body>
<div class="container mt-2">
    <header class="header">
        <h1 class="fw-bold text-dark">Daily Tech Intelligence Report</h1>
        <div class="designer">Designed by chipdory.hwang</div>
        <p class="text-muted mb-0">AI 자동 업데이트 리포트 (업데이트: {today})</p>
    </header>
    <div class="news-grid">
    """
    
    for i, news in enumerate(news_data):
        html_content += f"""
        <div class="news-card">
            <div class="d-flex justify-content-between mb-3 align-items-center">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#e2e8f0; font-weight:900; font-size:1.5rem;">{i+1:02d}</span>
            </div>
            <h5 class="fw-bold mb-3" style="line-height:1.4;">{news['title']}</h5>
            <p class="text-muted small" style="line-height:1.7;">{news['desc']}</p>
        </div>
        """

    html_content += """
    </div>
    <footer style="text-align:center; padding:60px 0; color:#cbd5e1; font-size:0.85rem;">
        © 2026 Designed by chipdory.hwang. All rights reserved.
    </footer>
</div>
</body>
</html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
