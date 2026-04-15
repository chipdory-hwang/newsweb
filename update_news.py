import feedparser
import datetime
import ssl
import re

# SSL 보안 설정
ssl._create_default_https_context = ssl._create_unverified_context

def clean_summary(text, title):
    """요약 내용을 풍성하게 정제하고 부족하면 보충"""
    if not text or len(text) < 20:
        # 요약이 너무 짧으면 제목을 활용해 풍성한 문장 생성
        return f"본 기사는 {title}에 관한 최신 핵심 소식을 다루고 있습니다. 기술 업계의 주요 변화와 시장 트렌드를 반영하는 중요한 이슈로, 상세 내용은 원문을 통해 심도 있게 확인하실 수 있습니다."
    
    # HTML 태그 제거 및 불필요한 문구 정리
    text = re.sub('<[^<]+?>', '', text)
    text = text.split("전체 기사 보기")[0]
    text = text.split("Google 뉴스에서")[0]
    
    # 최소 150자 이상 확보 (풍성함을 위해)
    if len(text) < 100:
        text += f" 관련하여 IT 업계와 과학계의 이목이 집중되고 있으며, 향후 기술 발전 방향에 중요한 지표가 될 것으로 전망됩니다."
        
    return text.strip()

def get_latest_news():
    all_news = []
    # 검색 쿼리를 더 구체적으로 변경 (더 풍성한 데이터를 유도)
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(target_url)
        for entry in feed.entries[:15]:
            if len(all_news) >= 10: break
            
            full_title = entry.title
            title, media = full_title, "테크리포트"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            # 핵심: summary와 description 중 더 긴 것을 선택
            raw_summary = entry.get('summary', '')
            if len(entry.get('description', '')) > len(raw_summary):
                raw_summary = entry.description
                
            summary = clean_summary(raw_summary, title)

            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": summary,
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
    <title>Tech Intelligence Deep Dive</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{ background: #f0f2f5; font-family: 'Pretendard', sans-serif; }}
        .header {{ 
            background: #fff; padding: 50px 20px; border-bottom: 8px solid #0056b3;
            text-align: center; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .designer {{ color: #0056b3; font-weight: 700; border: 2px solid #0056b3; display: inline-block; padding: 4px 15px; border-radius: 5px; margin-bottom: 10px; }}
        .news-grid {{ max-width: 800px; margin: 0 auto; padding: 0 15px 60px; }}
        .news-card {{ 
            background: #fff; border-radius: 20px; padding: 30px; margin-bottom: 25px; 
            box-shadow: 0 8px 25px rgba(0,0,0,0.06); border-left: 10px solid #0056b3;
            text-decoration: none; display: block; color: inherit;
        }}
        .badge-media {{ background: #e7f1ff; color: #0056b3; font-weight: 800; padding: 5px 15px; border-radius: 30px; font-size: 0.85rem; }}
        .card-title {{ font-size: 1.35rem; font-weight: 800; color: #111; margin: 15px 0; line-height: 1.4; }}
        .card-desc {{ font-size: 1.02rem; color: #444; line-height: 1.8; text-align: justify; background: #f8f9fa; padding: 20px; border-radius: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="designer">Designed by chipdory.hwang</div>
        <h1 class="fw-bold">Tech Intelligence Deep Dive</h1>
        <p class="text-muted small">반도체 · AI · IT 전문 리포트 ({today})</p>
    </div>
    <div class="news-grid">
    """
    for i, news in enumerate(news_data):
        html_content += f"""
        <a href="{news['link']}" target="_blank" class="news-card">
            <div class="d-flex justify-content-between">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#eee; font-weight:900; font-size:2rem;">{i+1:02d}</span>
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
