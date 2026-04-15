import feedparser
import datetime
import os

# 수집할 뉴스 RSS 주소 설정
RSS_FEEDS = {
    "전자신문": "https://www.etnews.com/section/main/rss",
    "디지털타임스": "http://www.dt.co.kr/rss/dt_all.xml",
    "인공지능신문": "https://www.aitimes.kr/rss/all.xml",
    "NYT(Tech)": "https://rss.nytimes.com/services/xml/rss/ntms/technology.xml",
    "IEEE Spectrum": "https://spectrum.ieee.org/rss/blog/spectrometer/fulltext"
}

def get_latest_news():
    all_news = []
    for media, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= 3: break
                
                # 요약 내용 정제
                summary = entry.summary if 'summary' in entry else entry.title
                summary = summary.replace('<br>', ' ').replace('</br>', ' ')
                summary = summary[:160] + "..." if len(summary) > 160 else summary
                
                all_news.append({
                    "media": media,
                    "title": entry.title.replace('"', "'"),
                    "desc": summary.replace('"', "'")
                })
                count += 1
        except Exception as e:
            print(f"{media} 수집 중 오류 발생: {e}")
    return all_news

def update_html(news_data):
    today = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Tech News Briefing</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {{ --primary-dark: #1a1a1a; --accent-blue: #0d6efd; }}
        body {{ background: #f4f7f6; font-family: 'Pretendard', -apple-system, sans-serif; word-break: keep-all; }}
        .header {{ text-align: center; padding: 50px 20px; background: #fff; border-bottom: 2px solid #eee; margin-bottom: 30px; }}
        .designer {{ font-size: 1.1rem; color: var(--accent-blue); font-weight: 600; margin-bottom: 15px; }}
        .news-card {{ background: #fff; border-radius: 16px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 6px solid var(--accent-blue); transition: 0.3s; }}
        .news-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }}
        .badge-media {{ background: #f8f9fa; color: #333; font-weight: 700; padding: 6px 12px; border-radius: 8px; border: 1px solid #eee; font-size: 0.8rem; }}
        @media (min-width: 993px) {{ .news-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }} }}
    </style>
</head>
<body>
<div class="container mt-2">
    <header class="header shadow-sm">
        <h1>Daily Tech Intelligence Report</h1>
        <div class="designer">Designed by chipdory.hwang</div>
        <p>AI 자동 업데이트 뉴스 리포트<br>(업데이트: {today})</p>
    </header>
    <div class="news-grid">
    """
    
    for i, news in enumerate(news_data):
        html_content += f"""
        <div class="news-card">
            <div class="d-flex justify-content-between mb-3">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#dee2e6; font-weight:900;">{i+1:02d}</span>
            </div>
            <div style="font-size:1.2rem; font-weight:800; margin-bottom:10px; line-height:1.4;">{news['title']}</div>
            <div style="color:#444; line-height:1.7; font-size:0.95rem; text-align:justify;">{news['desc']}</div>
        </div>
        """

    html_content += """
    </div>
    <footer style="text-align:center; padding:40px; color:#999; font-size:0.8rem;">
        본 페이지는 GitHub Actions를 통해 매일 자동 업데이트됩니다.
    </footer>
</div>
</body>
</html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    news = get_latest_news()
    if news:
        update_html(news)
if __name__ == "__main__":
    news = get_latest_news()
    
    # 만약 뉴스를 하나도 못 가져왔을 때를 대비한 기본 뉴스 추가
    if not news:
        news = [{
            "media": "안내",
            "title": "현재 뉴스를 불러오는 중입니다.",
            "desc": "잠시 후 다시 확인해 주세요. 수집 장치에 일시적인 지연이 발생했습니다."
        }]
    
    update_html(news)
