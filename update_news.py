import feedparser
import datetime

# RSS 주소 (안전한 주소들로 재세팅)
RSS_FEEDS = {
    "전자신문": "https://www.etnews.com/section/main/rss",
    "디지털타임스": "http://www.dt.co.kr/rss/dt_all.xml",
    "인공지능신문": "https://www.aitimes.kr/rss/all.xml",
    "NYT(Tech)": "https://rss.nytimes.com/services/xml/rss/ntms/technology.xml"
}

def get_latest_news():
    all_news = []
    for media, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for i, entry in enumerate(feed.entries[:3]): # 매체당 3개
                all_news.append({
                    "media": media,
                    "title": entry.title.replace('"', "'"),
                    "desc": entry.summary[:150].replace('"', "'") if 'summary' in entry else "상세 내용 요약 중..."
                })
        except:
            continue
    return all_news

def update_html(news_data):
    # 뉴스 데이터가 비었을 경우를 대비한 샘플 데이터
    if not news_data:
        news_data = [{"media": "시스템", "title": "뉴스 수집 중입니다.", "desc": "잠시 후 새로고침 해주세요."}]
        
    today = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Tech News</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background: #f4f7f6; font-family: 'Pretendard', sans-serif; padding: 20px; }}
        .header {{ text-align: center; padding: 40px; background: #fff; border-radius: 15px; margin-bottom: 30px; border-bottom: 5px solid #0d6efd; }}
        .news-card {{ background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Daily Tech Intelligence Report</h1>
            <h4 style="color: #0d6efd;">Designed by chipdory.hwang</h4>
            <p>최근 업데이트: {today}</p>
        </header>
        <div class="row">
    """
    for news in news_data:
        html_content += f"""
            <div class="col-md-4">
                <div class="news-card">
                    <span class="badge bg-primary mb-2">{news['media']}</span>
                    <h5 class="fw-bold">{news['title']}</h5>
                    <p class="small text-muted">{news['desc']}</p>
                </div>
            </div>"""
    
    html_content += "</div></div></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
