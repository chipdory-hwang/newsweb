import feedparser
import datetime
import ssl
import re
import requests
from bs4 import BeautifulSoup

# SSL 보안 에러 무시 설정
ssl._create_default_https_context = ssl._create_unverified_context

def get_full_summary(url):
    """기사 원문 링크에서 본문을 가져와 심층 요약함"""
    try:
        # 실제 브라우저와 거의 동일한 헤더 설정 (차단 우회 핵심)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 기사 본문이 위치할 확률이 높은 태그들 (언론사 공통 패턴)
        # 불필요한 태그(광고, 댓글, 스크립트) 미리 제거
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe']):
            s.decompose()

        # 본문 텍스트가 집중된 곳 찾기
        article_body = ""
        # 1순위: 기사 본문 전용 태그나 클래스 탐색
        body_candidates = soup.select('div[class*="article"], div[class*="content"], div[id*="article"], article')
        
        if body_candidates:
            # 후보군 중 가장 긴 텍스트를 가진 곳 선택
            article_body = max([c.get_text(separator=' ') for c in body_candidates], key=len)
        else:
            # 2순위: p 태그들 결합
            paragraphs = soup.find_all('p')
            article_body = " ".join([p.get_text() for p in paragraphs if len(p.get_text()) > 30])

        # 텍스트 정제
        content = re.sub(r'\s+', ' ', article_body).strip()
        
        # 기사 하단 기자 정보, 무단전재 등 불필요한 문구 제거
        content = re.sub(r'[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', content) # 이메일 제거
        
        # "충실한 요약"을 위해 최소 300자~500자 확보
        if len(content) > 500:
            return content[:500] + "..."
        elif len(content) > 100:
            return content
        return None
    except Exception as e:
        print(f"상세 요약 실패: {e}")
        return None

def get_latest_news():
    all_news = []
    # 검색어 최적화: IT 기술 핵심 키워드
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(target_url)
        
        for entry in feed.entries:
            if len(all_news) >= 10: break
            
            full_title = entry.title
            title, media = full_title, "테크리포트"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            # 기사 원문 링크
            news_link = entry.link
            
            # [핵심] 본문 딥 스크래핑 시도
            detailed_summary = get_full_summary(news_link)
            
            # 본문 추출 실패 시 RSS 기본 요약이라도 활용
            if not detailed_summary:
                rss_desc = re.sub('<[^<]+?>', '', entry.summary).split("전체 기사 보기")[0]
                detailed_summary = f"[본문 추출 제한] {rss_desc} (자세한 내용은 원문을 참고하세요)"

            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": detailed_summary.strip(),
                "link": news_link
            })
    except Exception as e:
        print(f"뉴스 목록 수집 실패: {e}")
            
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
    <title>Tech Deep Dive Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        body {{ background: #f4f6f9; font-family: 'Pretendard', sans-serif; color: #334155; }}
        .header {{ 
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 60px 20px; 
            text-align: center; margin-bottom: 40px; color: white; box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .designer {{ border: 1.5px solid #38bdf8; color: #38bdf8; display: inline-block; padding: 4px 16px; border-radius: 50px; margin-bottom: 15px; font-weight: 600; font-size: 0.9rem; }}
        .news-grid {{ max-width: 850px; margin: 0 auto; padding: 0 15px 80px; }}
        .news-card {{ 
            background: #fff; border-radius: 24px; padding: 35px; margin-bottom: 30px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
            text-decoration: none; display: block; color: inherit; transition: all 0.3s ease;
        }}
        .news-card:hover {{ transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); border-color: #38bdf8; }}
        .badge-media {{ background: #f0f9ff; color: #0369a1; font-weight: 800; padding: 6px 14px; border-radius: 8px; font-size: 0.85rem; }}
        .card-title {{ font-size: 1.45rem; font-weight: 800; color: #0f172a; margin: 20px 0 15px; line-height: 1.4; }}
        .card-desc {{ font-size: 1.05rem; color: #475569; line-height: 1.85; text-align: justify; background: #f8fafc; padding: 20px; border-radius: 15px; }}
        .footer {{ text-align: center; color: #94a3b8; padding-bottom: 50px; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="designer">Designed by chipdory.hwang</div>
        <h1 class="fw-bold mb-3">Tech Intelligence Deep Dive</h1>
        <p class="opacity-75 mb-0">인공지능 · 반도체 · 과학기술 전문 분석 리포트</p>
        <p class="small mt-2 opacity-50">업데이트: {today}</p>
    </div>
    <div class="news-grid">
    """
    for i, news in enumerate(news_data):
        html_content += f"""
        <a href="{news['link']}" target="_blank" class="news-card">
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#f1f5f9; font-weight:900; font-size:2.5rem;">{i+1:02d}</span>
            </div>
            <div class="card-title">{news['title']}</div>
            <div class="card-desc">{news['desc']}</div>
            <div class="mt-3 text-end" style="color:#0369a1; font-weight:700; font-size:0.9rem;">원문 전체보기 →</div>
        </a>
        """
    html_content += """
    </div>
    <div class="footer">본 리포트는 매일 아침 6시에 신규 데이터를 기반으로 생성됩니다.</div>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
