import feedparser
import datetime
import ssl
import re
import os

# SSL 보안 에러 무시 설정
ssl._create_default_https_context = ssl._create_unverified_context

def get_latest_news():
    all_news = []
    # 가장 차단이 적은 구글 뉴스 통합 검색 주소 (반도체, AI, IT, 과학)
    # 한국어(hl=ko)와 한국 지역(gl=KR) 설정 포함
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    # 브라우저처럼 보이게 하는 헤더 정보
    user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
    
    try:
        feed = feedparser.parse(target_url, agent=user_agent)
        
        for entry in feed.entries:
            if len(all_news) >= 10: break # 딱 10건만 수집
            
            # 매체명과 제목 분리 (구글 뉴스는 '제목 - 매체명' 형식)
            full_title = entry.title
            if " - " in full_title:
                title_parts = full_title.rsplit(" - ", 1)
                title = title_parts[0]
                media = title_parts[1]
            else:
                title = full_title
                media = "뉴스"

            # 요약 내용 정제 (HTML 태그 제거)
            summary = re.sub('<[^<]+?>', '', entry.summary) if 'summary' in entry else "상세 내용은 클릭하여 확인하세요."
            
            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": summary[:150].strip() + "..."
            })
    except Exception as e:
        print(f"데이터 수집 중 에러 발생: {e}")
            
    return all_news

def update_html(news_data):
    # [핵심] 수집된 뉴스가 없으면 파일 생성 과정을 중단하여 기존 index.html을 보존함
    if not news_data or len(news_data) < 1:
        print("수집된 뉴스가 없어 업데이트를 취소합니다. 기존 파일을 유지합니다.")
        return

    today = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Tech Intelligence</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background: #f0f2f5; font-family: 'Pretendard', -apple-system, sans-serif; }}
        .header {{ text-align: center; padding: 40px 20px; background: #fff; border-bottom: 6px solid #0056b3; margin-bottom: 25px; }}
        .designer {{ font-size: 1.1rem; color: #0056b3; font-weight: 700; margin-bottom: 8px; }}
        .news-grid {{ display: flex; flex-direction: column; gap: 15px; padding: 0 15px 40px; max-width: 800px; margin: 0 auto; }}
        .news-card {{ background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 5px solid #0056b3; }}
        .badge-media {{ background: #e7f1ff; color: #0056b3; font-weight: 700; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; }}
        .card-title {{ font-size: 1.1rem; font-weight: 800; color: #1a1a1a; margin: 10px 0; line-height: 1.4; }}
        .card-desc {{ font-size: 0.9rem; color: #4b5563; line-height: 1.6; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="designer">Designed by chipdory.hwang</div>
        <h1 class="fw-bold" style="font-size: 1.5rem;">Tech Intelligence Report</h1>
        <p class="text-muted small mb-0">분야: 반도체 · AI · IT · 과학 ({today})</p>
    </header>
    <div class="news-grid">
    """
    
    for i, news in enumerate(news_data):
        html_content += f"""
        <div class="news-card">
            <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge-media text-truncate" style="max-width: 150px;">{news['media']}</span>
                <span style="color:#dee2e6; font-weight:900;">{i+1:02d}</span>
            </div>
            <div class="card-title">{news['title']}</div>
            <div class="card-desc">{news['desc']}</div>
        </div>
        """

    html_content += """
    </div>
    <footer style="text-align:center; padding:30px; color:#999; font-size:0.75rem;">
        본 리포트는 매일 자동으로 갱신됩니다.
    </footer>
</body>
</html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
