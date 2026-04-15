import feedparser
import datetime
import ssl
import re

# SSL 보안 설정
ssl._create_default_https_context = ssl._create_unverified_context

def get_latest_news():
    all_news = []
    # 이전 사이트와 동일한 표준 구글 뉴스 RSS 주소
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(target_url)
        
        for entry in feed.entries[:10]:
            # 1. 제목과 매체 분리
            full_title = entry.title
            title, media = full_title, "뉴스"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            # 2. RSS 원본 요약본 가져오기 (가공 최소화)
            # summary_detail 혹은 summary에 담긴 원문을 그대로 사용합니다.
            raw_desc = entry.get('summary', '')
            
            # HTML 태그만 제거 (내용 요약이나 문구 추가 절대 안 함)
            clean_desc = re.sub('<[^<]+?>', '', raw_desc)
            
            # 구글 뉴스 특유의 꼬리말만 잘라내기
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
        body {{ background: #f8f9fa; font-family: 'Pretendard', sans-serif; color: #333; }}
        .header {{ 
            text-align: center; padding: 40px 20px; background: #fff; 
            border-bottom: 6px solid #0056b3; margin-bottom: 30px; 
        }}
        .designer {{ color: #0056b3; font-weight: 700; border: 2px solid #0056b3; display: inline-block; padding: 3px 12px; border-radius: 5px; margin-bottom: 10px; font-size: 0.9rem; }}
        .news-grid {{ max-width: 800px; margin: 0 auto; padding: 0 15px 60px; }}
        .news-card {{ 
            background: #fff; border-radius: 15px; padding: 25px; margin-bottom: 20px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 6px solid #0056b3;
            text-decoration: none; display: block; color: inherit;
        }}
        .badge-media {{ background: #e7f1ff; color: #0056b3; font-weight: 700; padding: 4px 10px; border-radius: 5px; font-size: 0.8rem; }}
        .card-title {{ font-size: 1.25rem; font-weight: 800; color: #000; margin: 12px 0; line-height: 1.4; }}
        .card-desc {{ font-size: 1rem; color: #444; line-height: 1.7; text-align: justify; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="designer">Designed by chipdory.hwang</div>
        <h2 class="fw-bold">Tech Intelligence Report</h2>
        <p class="text-muted small mb-0">{today} 업데이트</p>
    </header>
    <div class="news-grid">
    """
    for i, news in enumerate(news_data):
        html_content += f"""
        <a href="{news['link']}" target="_blank" class="news-card">
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#eee; font-weight:900; font-size:1.5rem;">{i+1:02d}</span>
            </div>
            <div class="card-title">{news['title']}</div>
            <div class="card-desc">{news['desc']}</div>
        </a>
        """
    html_content += "</div></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
