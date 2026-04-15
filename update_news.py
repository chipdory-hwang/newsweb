import feedparser
import datetime
import ssl
import re

# SSL 보안 에러 무시 설정
ssl._create_default_https_context = ssl._create_unverified_context

def clean_text(text):
    """HTML 태그 제거 및 불필요한 공백 정리"""
    if not text: return ""
    text = re.sub('<[^<]+?>', '', text) # 모든 HTML 태그 제거
    text = text.replace('&nbsp;', ' ').replace('&quot;', '"').replace('&amp;', '&')
    return text.strip()

def get_latest_news():
    all_news = []
    # 검색어를 더 구체화하여 풍성한 기사를 유도 (최신순 정렬)
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
    
    try:
        feed = feedparser.parse(target_url, agent=user_agent)
        
        for entry in feed.entries[:12]: # 중복 대비 12개 수집 후 10개 추출
            if len(all_news) >= 10: break
            
            # 매체명과 제목 분리
            full_title = entry.title
            title = full_title
            media = "IT 이슈"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            # 요약 내용 보강
            # RSS의 'summary' 혹은 'description'에서 더 긴 내용을 선택
            raw_content = entry.get('summary', '') or entry.get('description', '')
            content = clean_text(raw_content)
            
            # 구글 뉴스 특유의 '매체별 링크 모음' 텍스트 제거
            if "전체 기사 보기" in content:
                content = content.split("전체 기사 보기")[0]

            # 내용이 너무 짧으면 제목을 활용해 문장 완성
            if len(content) < 40:
                content = f"[{media} 핵심 보도] {title} 관련 최신 소식입니다. 기술 업계의 주요 흐름을 반영하는 뉴스입니다."

            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": content.strip()
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
        body {{ background: #f4f7fa; font-family: 'Pretendard', sans-serif; color: #333; }}
        .header {{ 
            text-align: center; padding: 50px 20px; background: linear-gradient(135deg, #0056b3 0%, #003d7a 100%); 
            color: white; border-radius: 0 0 30px 30px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .designer {{ font-size: 1rem; opacity: 0.9; font-weight: 500; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.4); display: inline-block; padding: 2px 12px; border-radius: 20px; }}
        .news-grid {{ max-width: 850px; margin: 0 auto; padding: 0 15px 60px; }}
        .news-card {{ 
            background: #fff; border-radius: 18px; padding: 28px; margin-bottom: 25px; 
            box-shadow: 0 10px 20px rgba(0,0,0,0.05); border: 1px solid #eef2f6;
            transition: all 0.3s ease;
        }}
        .badge-media {{ background: #e7f1ff; color: #0056b3; font-weight: 700; padding: 6px 14px; border-radius: 10px; font-size: 0.85rem; }}
        .card-title {{ font-size: 1.3rem; font-weight: 800; color: #111; margin: 18px 0 12px; line-height: 1.5; }}
        .card-desc {{ font-size: 1.05rem; color: #555; line-height: 1.8; text-align: justify; word-break: break-all; }}
        .footer {{ text-align: center; padding-bottom: 40px; color: #888; font-size: 0.9rem; }}
        @media (max-width: 768px) {{
            .header {{ padding: 40px 15px; }}
            .card-title {{ font-size: 1.15rem; }}
            .card-desc {{ font-size: 0.98rem; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="designer">Designed by chipdory.hwang</div>
        <h1 class="fw-bold">Tech Intelligence Report</h1>
        <p class="mb-0 opacity-75">{today} | 반도체 · AI · IT · 과학</p>
    </header>
    <div class="news-grid">
    """
    
    for i, news in enumerate(news_data):
        html_content += f"""
        <div class="news-card">
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#e9ecef; font-weight:900; font-size:1.8rem;">{i+1:02d}</span>
            </div>
            <div class="card-title">{news['title']}</div>
            <div class="card-desc">{news['desc']}</div>
        </div>
        """

    html_content += """
    </div>
    <div class="footer">
        매일 오전 6시 자동으로 업데이트 됩니다.
    </div>
</body>
</html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
