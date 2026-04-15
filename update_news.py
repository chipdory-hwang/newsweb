import feedparser
import datetime
import ssl
import re
import sys

# 출력 인코딩 강제 설정 (이모지 깨짐 방지)
sys.stdout.reconfigure(encoding='utf-8')
ssl._create_default_https_context = ssl._create_unverified_context

def get_latest_news():
    all_news = []
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99+OR+%EA%B8%B0%EC%88%A0&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(target_url)
        for entry in feed.entries[:10]:
            full_title = entry.title
            title, media = full_title, "뉴스"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            all_news.append({
                "media": media,
                "title": title.strip(),
                "link": entry.link
            })
    except Exception as e:
        print(f"Error during news fetching: {e}")
    return all_news

def update_html(news_data):
    if not news_data: return
    today = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    
    # HTML 템플릿 - 요청하신 디자인 반영
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Tech Intelligence Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{ background: #f4f7f6; font-family: 'Pretendard', sans-serif; color: #333; }}
        .header {{ 
            text-align: center; padding: 45px 20px; background: #fff; 
            border-bottom: 1px solid #eee; margin-bottom: 30px; 
        }}
        .header h2 {{ 
            font-weight: 900; color: #111; margin-bottom: 10px; 
            text-decoration: underline; text-underline-offset: 8px;
            text-decoration-thickness: 3px; text-decoration-color: #0056b3;
        }}
        .category {{ font-weight: 700; font-size: 0.95rem; color: #444; margin-bottom: 15px; }}
        .update-info {{ font-size: 0.85rem; color: #777; margin-bottom: 3px; }}
        .designer {{ font-size: 0.85rem; color: #0056b3; font-weight: 600; }}
        .news-grid {{ max-width: 600px; margin: 0 auto; padding: 0 15px 60px; }}
        .news-card {{ 
            background: #fff; border-radius: 14px; margin-bottom: 18px; 
            box-shadow: 0 3px 12px rgba(0,0,0,0.06); overflow: hidden;
            border: 1px solid #eee; text-decoration: none; display: block; color: inherit;
        }}
        .card-table {{ width: 100%; border-collapse: collapse; }}
        .row-top {{ background: #f8f9fa; border-bottom: 1px solid #f0f0f0; }}
        .cell-num {{ width: 55px; text-align: center; font-weight: 900; color: #0056b3; font-size: 1.15rem; padding: 12px 0; }}
        .cell-media {{ padding: 12px 10px; font-weight: 700; color: #555; font-size: 0.9rem; }}
        .row-content {{ padding: 20px; }}
        .card-title {{ font-size: 1.15rem; font-weight: 800; color: #111; line-height: 1.5; margin-bottom: 15px; }}
        .link-btn {{ color: #0056b3; font-weight: 700; font-size: 0.95rem; border-top: 1px solid #f1f1f1; padding-top: 12px; text-align: right; }}
    </style>
</head>
<body>
    <header class="header">
        <h2>Daily Tech Intelligence Report</h2>
        <div class="category">반도체 / AI / IT / 기술 / 과학</div>
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
                <div class="link-btn">원본확인 🖱️</div>
            </div>
        </a>
        """
        
    html_content += "</div></body></html>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
