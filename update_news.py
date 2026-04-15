import feedparser
import datetime
import ssl
import re

# SSL 보안 설정
ssl._create_default_https_context = ssl._create_unverified_context

def get_latest_news():
    all_news = []
    # 최적화된 구글 뉴스 RSS 주소
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(target_url)
        
        for entry in feed.entries[:10]:
            # 제목과 매체 분리
            full_title = entry.title
            title, media = full_title, "뉴스"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            all_news.append({
                "media": media.strip(),
                "title": title.strip(),
                "link": entry.link
            })
    except Exception as e:
        print(f"데이터 수집 중 에러: {e}")
            
    return all_news

def update_html(news_data):
    if not news_data: return
    today = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech Intelligence Briefing</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{ background: #ffffff; font-family: 'Pretendard', sans-serif; color: #333; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #333; }}
        .designer {{ font-weight: 700; color: #0056b3; margin-bottom: 5px; display: block; }}
        .news-table {{ width: 100%; max-width: 1000px; margin: 0 auto; border-collapse: collapse; }}
        .news-table th {{ background: #f8f9fa; color: #111; font-weight: 800; border-top: 2px solid #333; border-bottom: 1px solid #ddd; padding: 12px; text-align: center; }}
        .news-table td {{ padding: 15px 10px; border-bottom: 1px solid #eee; vertical-align: middle; }}
        .num {{ text-align: center; font-weight: 600; color: #888; width: 50px; }}
        .media {{ text-align: center; font-weight: 700; color: #0056b3; width: 120px; }}
        .title {{ font-weight: 500; color: #222; }}
        .source-btn {{ 
            display: inline-block; padding: 4px 10px; background: #333; color: #fff; 
            text-decoration: none; border-radius: 4px; font-size: 0.8rem; font-weight: 600;
            white-space: nowrap;
        }}
        .source-btn:hover {{ background: #0056b3; color: #fff; }}
        @media (max-width: 600px) {{
            .news-table {{ font-size: 0.85rem; }}
            .media {{ width: 80px; }}
            .source-btn {{ padding: 3px 6px; font-size: 0.7rem; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <span class="designer">Designed by chipdory.hwang</span>
        <h2 class="fw-bold">Tech Intelligence Briefing</h2>
        <p class="text-muted small mb-0">분야: 반도체 · AI · IT · 과학 | {today}</p>
    </header>

    <div class="table-responsive">
        <table class="news-table">
            <thead>
                <tr>
                    <th>번호</th>
                    <th>매체</th>
                    <th>제목</th>
                    <th>원본출처</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, news in enumerate(news_data):
        html_content += f"""
                <tr>
                    <td class="num">{i+1:02d}</td>
                    <td class="media">{news['media']}</td>
                    <td class="title">{news['title']}</td>
                    <td class="text-center">
                        <a href="{news['link']}" target="_blank" class="source-btn">원본확인</a>
                    </td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>
    </div>
    <footer style="text-align:center; margin-top:50px; color:#999; font-size:0.8rem;">
        매일 아침 자동으로 갱신되는 텍스트 기반 브리핑 서비스입니다.
    </footer>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
