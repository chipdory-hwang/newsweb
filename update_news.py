import feedparser
import datetime
import ssl
import re

# SSL 보안 설정
ssl._create_default_https_context = ssl._create_unverified_context

def get_latest_news():
    all_news = []
    # 최적화된 구글 뉴스 RSS 주소
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99+OR+%EA%B8%B0%EC%88%A0&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(target_url)
        
        for entry in feed.entries[:10]:
            full_title = entry.title
            title, media = full_title, "뉴스"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            # RSS 원본 요약본 (가공 없이 태그만 제거)
            raw_desc = entry.get('summary', '')
            clean_desc = re.sub('<[^<]+?>', '', raw_desc)
            clean_desc = clean_desc.split("전체 기사 보기")[0].strip()

            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": clean_desc,
                "link": entry.link
            })
    except Exception as e:
        print(f"Error: {e}")
            
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
    <title>Tech Intelligence Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{ background: #f4f7f6; font-family: 'Pretendard', sans-serif; color: #333; }}
        .header {{ 
            text-align: center; padding: 40px 20px; background: #fff; 
            border-bottom: 1px solid #eee; margin-bottom: 30px; 
        }}
        .header h2 {{ font-weight: 800; color: #111; margin-bottom: 5px; }}
        .update-info {{ font-size: 0.85rem; color: #666; margin-bottom: 2px; }}
        .designer {{ font-size: 0.85rem; color: #0056b3; font-weight: 600; }}
        
        .news-grid {{ max-width: 600px; margin: 0 auto; padding: 0 15px 60px; }}
        
        /* 모바일 최적화 표 스타일 카드 */
        .news-card {{ 
            background: #fff; border-radius: 12px; margin-bottom: 20px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); overflow: hidden;
            border: 1px solid #eee; text-decoration: none; display: block; color: inherit;
        }}
        .card-table {{ width: 100%; border-collapse: collapse; }}
        .row-top {{ background: #fcfcfc; border-bottom: 1px solid #f0f0f0; }}
        .cell-num {{ width: 50px; text-align: center; font-weight: 900; color: #0056b3; font-size: 1.1rem; padding: 12px 0; }}
        .cell-media {{ padding: 12px 10px; font-weight: 700; color: #555; font-size: 0.9rem; }}
        .row-content {{ padding: 15px; display: block; }}
        .card-title {{ font-size: 1.1rem; font-weight: 800; color: #000; line-height: 1.5; margin-bottom: 8px; }}
        .card-desc {{ font-size: 0.95rem; color: #444; line-height: 1.6; text-align: justify; margin-bottom: 12px; }}
        .link-btn {{ color: #0056b3; font-weight: 700; font-size: 0.85rem; border-top: 1px solid #f0f0f0; padding-top: 10px; display: block; }}
    </style>
</head>
<body>
    <header class="header">
        <h2>Tech Intelligence</h2>
        <p class="mb-2" style="font-weight:600; font-size:0.95rem; color:#444;">반도체 / AI / IT / 기술 / 과학</p>
        <p class="update-info">최종 업데이트: {today}</p>
        <p class="designer">Designed by chipdory.hwang</p>
    </header>
    
    <div class="news-grid">
    """
    for i, news in enumerate(news_data):
        html_content += f"""
        <a href="{news['link']}" target="_blank" class="news-card">
            <table class="card-table">
                <tr class="row-top">
                    <td class="cell-num">{i+1:02d}</td>
                    <td class="cell-media">{news['media']}</td>
                </tr>
            </table>
            <div class="row-content">
                <div class="card-title">{news['title']}</div>
                <div class="card-desc">{news['desc']}</div>
                <div class="link-btn">원본확인 →</div>
            </div>
        </a>
        """
    html_content += """
    </div>
    <footer style="text-align:center; padding-bottom:40px; color:#999; font-size:0.8rem;">
        매일 오전 6시 자동으로 업데이트 됩니다.
    </footer>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
