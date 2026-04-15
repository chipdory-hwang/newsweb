import feedparser
import datetime
import ssl
import re

# SSL 인증서 문제 해결
ssl._create_default_https_context = ssl._create_unverified_context

def get_latest_news():
    all_news = []
    # 구글 뉴스 RSS (IT/기술 분야 중심)
    # 한국어 뉴스 중 '반도체', 'AI', 'IT' 키워드 추출
    queries = [
        ("반도체", "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4&hl=ko&gl=KR&ceid=KR:ko"),
        ("AI", "https://news.google.com/rss/search?q=AI&hl=ko&gl=KR&ceid=KR:ko"),
        ("IT/과학", "https://news.google.com/rss/search?q=%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko")
    ]
    
    for category, url in queries:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # 카테고리당 5개씩 총 15개
                # 매체명 추출 (제목 끝의 ' - 매체명' 부분 활용)
                title_split = entry.title.rsplit(' - ', 1)
                title = title_split[0]
                media = title_split[1] if len(title_split) > 1 else category
                
                all_news.append({
                    "media": media,
                    "title": title,
                    "desc": entry.title # 구글 뉴스 RSS는 요약이 제목과 같은 경우가 많음
                })
        except:
            continue
    return all_news

def update_html(news_data):
    # 데이터가 정말 없을 때만 최후의 수단으로 고정 데이터 사용
    if not news_data:
        news_data = [{"media": "알림", "title": "뉴스를 불러오는 중입니다.", "desc": "잠시 후 다시 확인해 주세요."}]
        
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
        body {{ background: #f8fafc; font-family: 'Pretendard', sans-serif; }}
        .header {{ text-align: center; padding: 60px 20px; background: #fff; border-bottom: 5px solid #0d6efd; margin-bottom: 40px; }}
        .news-card {{ background: #fff; border-radius: 15px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 6px solid #0d6efd; }}
        .designer {{ font-size: 1.1rem; color: #0d6efd; font-weight: 600; margin-bottom: 15px; }}
        @media (min-width: 992px) {{ .news-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; }} }}
    </style>
</head>
<body>
<div class="container">
    <header class="header">
        <h1 class="fw-bold">Daily Tech Intelligence Report</h1>
        <div class="designer">Designed by chipdory.hwang</div>
        <p class="text-muted mb-0">AI 자동 업데이트 (최종 갱신: {today})</p>
    </header>
    <div class="news-grid">
    """
    
    for i, news in enumerate(news_data):
        html_content += f"""
        <div class="news-card">
            <span class="badge bg-light text-dark mb-2 border">{news['media']}</span>
            <h5 class="fw-bold mb-3">{news['title']}</h5>
            <p class="text-muted small mb-0">{news['desc']}</p>
        </div>"""

    html_content += "</div></div></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
