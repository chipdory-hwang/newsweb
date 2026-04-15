import feedparser
import datetime
import ssl
import re

# SSL 인증서 문제 해결
ssl._create_default_https_context = ssl._create_unverified_context

def get_latest_news():
    all_news = []
    # 요청하신 5개 주요 매체 RSS
    RSS_FEEDS = {
        "전자신문": "https://www.etnews.com/section/main/rss",
        "디지털타임스": "http://www.dt.co.kr/rss/dt_all.xml",
        "인공지능신문": "https://www.aitimes.kr/rss/all.xml",
        "NYT(Tech)": "https://rss.nytimes.com/services/xml/rss/ntms/technology.xml",
        "IEEE Spectrum": "https://spectrum.ieee.org/rss/blog/spectrometer/fulltext"
    }
    
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    for media, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url, agent=user_agent)
            # 매체별로 딱 3개씩만 발췌
            for entry in feed.entries[:3]:
                # HTML 태그 제거 및 요약 정리
                summary = entry.summary if 'summary' in entry else "상세 내용은 원문을 확인해주세요."
                summary = re.sub('<[^<]+?>', '', summary) # 태그 제거
                summary = summary.replace('&nbsp;', ' ').strip()
                summary = summary[:180] + "..." if len(summary) > 180 else summary
                
                all_news.append({
                    "media": media,
                    "title": entry.title.strip(),
                    "desc": summary
                })
        except:
            continue
    return all_news

def update_html(news_data):
    today = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Tech Intelligence Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {{ --primary-blue: #0d6efd; --bg-gray: #f4f7f6; }}
        body {{ background: var(--bg-gray); font-family: 'Pretendard', -apple-system, sans-serif; word-break: keep-all; }}
        
        /* 헤더 스타일 */
        .header {{ text-align: center; padding: 50px 20px; background: #fff; border-bottom: 5px solid var(--primary-blue); margin-bottom: 30px; shadow: 0 4px 10px rgba(0,0,0,0.05); }}
        .header h1 {{ font-weight: 800; font-size: 1.8rem; color: #1a1a1a; margin-bottom: 10px; }}
        .designer {{ font-size: 1rem; color: var(--primary-blue); font-weight: 600; margin-bottom: 15px; letter-spacing: 0.5px; }}
        .update-time {{ font-size: 0.9rem; color: #777; }}

        /* 모바일 최적화: 카드 레이아웃 */
        .news-grid {{ display: flex; flex-direction: column; gap: 20px; padding-bottom: 50px; }}
        .news-card {{ 
            background: #fff; border-radius: 16px; padding: 25px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 6px solid var(--primary-blue);
            transition: transform 0.2s ease;
        }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .badge-media {{ background: #f8f9fa; color: #333; font-weight: 700; padding: 5px 12px; border-radius: 8px; border: 1px solid #eee; font-size: 0.75rem; }}
        .card-no {{ font-weight: 900; color: #dee2e6; font-size: 1.4rem; }}
        .card-title {{ font-size: 1.2rem; font-weight: 800; color: #111; margin-bottom: 12px; line-height: 1.4; }}
        .card-desc {{ font-size: 0.95rem; color: #444; line-height: 1.7; text-align: justify; }}

        /* PC 버전: 3열 배치 */
        @media (min-width: 992px) {{
            .news-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; }}
            .header h1 {{ font-size: 2.4rem; }}
        }}
    </style>
</head>
<body>
<div class="container mt-2">
    <header class="header">
        <h1>Daily Tech Intelligence Report</h1>
        <div class="designer">Designed by chipdory.hwang</div>
        <p class="update-time">AI 자동 뉴스 브리핑 (최종 업데이트: {today})</p>
    </header>

    <div class="news-grid">
    """
    
    for i, news in enumerate(news_data):
        html_content += f"""
        <div class="news-card">
            <div class="card-header">
                <span class="badge-media">{news['media']}</span>
                <span class="card-no">{i+1:02d}</span>
            </div>
            <div class="card-title">{news['title']}</div>
            <div class="card-desc">{news['desc']}</div>
        </div>
        """

    html_content += """
    </div>
    <footer style="text-align:center; padding:40px; color:#aaa; font-size:0.8rem;">
        © 2026 Designed by chipdory.hwang | Powered by GitHub Actions
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
