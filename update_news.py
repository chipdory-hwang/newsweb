import feedparser
import datetime
import ssl
import re

# SSL 보안 설정
ssl._create_default_https_context = ssl._create_unverified_context

def clean_html(raw_html):
    """HTML 태그 제거 및 구글 뉴스 특유의 불필요한 문구 정리"""
    if not raw_html: return ""
    # 태그 제거
    clean_text = re.sub('<[^<]+?>', '', raw_html)
    # 구글 뉴스 RSS 하단의 관련 기사 링크 텍스트 제거
    clean_text = clean_text.split("전체 기사 보기")[0]
    clean_text = clean_text.split("Google 뉴스에서")[0]
    return clean_text.strip()

def get_latest_news():
    all_news = []
    # 이전 사이트에서 사용했던 것과 유사한 최적화된 구글 뉴스 쿼리
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        # RSS 피드 파싱
        feed = feedparser.parse(target_url)
        
        for entry in feed.entries[:15]: # 중복 제외 후 10개를 뽑기 위해 넉넉히 수집
            if len(all_news) >= 10: break
            
            # 제목과 매체 분리
            full_title = entry.title
            title, media = full_title, "테크리포트"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            # 요약 데이터 추출 (이전 버전의 핵심 로직)
            # 구글 RSS의 summary는 이미 어느 정도 요약된 본문을 포함하고 있습니다.
            summary = clean_html(entry.summary)
            
            # 만약 요약이 너무 짧으면 description 시도
            if len(summary) < 50 and 'description' in entry:
                summary = clean_html(entry.description)

            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": summary,
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
    <title>Tech Intelligence Deep Dive</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{ background: #f8f9fa; font-family: 'Pretendard', sans-serif; color: #212529; }}
        .header {{ 
            background: #ffffff; padding: 50px 20px; border-bottom: 8px solid #0056b3;
            text-align: center; margin-bottom: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .designer {{ color: #0056b3; font-weight: 700; border: 2px solid #0056b3; display: inline-block; padding: 4px 15px; border-radius: 5px; margin-bottom: 15px; }}
        .news-grid {{ max-width: 900px; margin: 0 auto; padding: 0 15px 80px; }}
        .news-card {{ 
            background: #fff; border-radius: 20px; padding: 35px; margin-bottom: 30px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-left: 8px solid #0056b3;
            text-decoration: none; display: block; color: inherit; transition: all 0.2s ease-in-out;
        }}
        .news-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.12); }}
        .badge-media {{ background: #f1f8ff; color: #0056b3; font-weight: 800; padding: 6px 16px; border-radius: 30px; font-size: 0.9rem; }}
        .card-title {{ font-size: 1.4rem; font-weight: 800; color: #1a1a1a; margin: 20px 0 15px; line-height: 1.4; }}
        .card-desc {{ font-size: 1.05rem; color: #444; line-height: 1.9; text-align: justify; border-top: 1px solid #f0f0f0; padding-top: 15px; }}
        .footer {{ text-align: center; color: #95a5a6; padding-bottom: 50px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="designer">Designed by chipdory.hwang</div>
        <h1 class="fw-bold">Tech Intelligence Deep Dive</h1>
        <p class="text-muted mb-0">인공지능·반도체 전문 리포트 | {today}</p>
    </div>
    <div class="news-grid">
    """
    for i, news in enumerate(news_data):
        html_content += f"""
        <a href="{news['link']}" target="_blank" class="news-card">
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#eee; font-weight:900; font-size:2rem;">{i+1:02d}</span>
            </div>
            <div class="card-title">{news['title']}</div>
            <div class="card-desc">{news['desc']}</div>
            <div style="margin-top: 15px; color: #0056b3; font-weight: 700; font-size: 0.9rem;">원문 기사 읽기 →</div>
        </a>
        """
    html_content += """
    </div>
    <div class="footer">매일 아침 6시 업데이트됩니다.</div>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
