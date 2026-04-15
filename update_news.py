import feedparser
import datetime
import ssl
import re
import requests
from bs4 import BeautifulSoup

# SSL 보안 에러 무시 설정
ssl._create_default_https_context = ssl._create_unverified_context

def get_full_summary(url):
    """기사 원문 링크에서 본문을 지능적으로 추출하여 요약함"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        
        # 1. 페이지 요청
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code != 200:
            return None
            
        # 인코딩 설정 (한글 깨짐 방지)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. 불필요한 요소 선제거
        for s in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe', 'button', 'form']):
            s.decompose()

        # 3. 본문 추출 핵심 로직: 텍스트가 밀집된 컨테이너 찾기
        # div, section, article 중 텍스트 길이가 가장 긴 요소를 본문으로 간주
        best_element = None
        max_length = 0
        
        for tag in ['div', 'section', 'article']:
            elements = soup.find_all(tag)
            for el in elements:
                # 해당 요소 내의 순수 텍스트 길이 측정
                text_len = len(el.get_text(strip=True))
                if text_len > max_length:
                    # 너무 광범위한 부모 태그(body 등) 방지를 위해 자식 요소 중 더 긴 게 있는지 체크
                    max_length = text_len
                    best_element = el

        if not best_element:
            return None

        # 4. 추출된 요소 내에서 p, div 등 의미 있는 문장들만 결합
        paragraphs = best_element.find_all(['p', 'div'], recursive=True)
        lines = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 25]
        
        # 중복 문장 제거 및 결합
        seen = set()
        clean_lines = []
        for line in lines:
            if line not in seen:
                clean_lines.append(line)
                seen.add(line)
        
        full_text = " ".join(clean_lines)
        
        # 5. 불필요한 정크 문구 제거 (기자, 무단전재, 광고 등)
        full_text = re.sub(r'[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', full_text) # 이메일 제거
        full_text = re.sub(r'\(.*?\)|\{.*?\}|\[.*?\]', '', full_text) # 괄호 안의 광고성 문구 제거
        
        # 충실한 요약을 위해 450~500자 반환
        if len(full_text) > 450:
            return full_text[:450].strip() + "..."
        elif len(full_text) > 100:
            return full_text.strip()
        return None

    except Exception as e:
        print(f"추출 실패: {url} | 사유: {e}")
        return None

def get_latest_news():
    all_news = []
    # 검색 키워드 고정
    target_url = "https://news.google.com/rss/search?q=%EB%B0%98%EB%8F%84%EC%B2%B4+OR+AI+OR+IT+OR+%EA%B3%BC%ED%95%99&hl=ko&gl=KR&ceid=KR:ko"
    
    try:
        feed = feedparser.parse(target_url)
        for entry in feed.entries[:15]: # 중복 및 실패 대비 15개 시도
            if len(all_news) >= 10: break
            
            full_title = entry.title
            title, media = full_title, "테크리포트"
            if " - " in full_title:
                parts = full_title.rsplit(" - ", 1)
                title, media = parts[0], parts[1]

            # 상세 요약 시도
            detailed_summary = get_full_summary(entry.link)
            
            # 실패 시 RSS 원본 요약이라도 정제해서 사용
            if not detailed_summary:
                rss_desc = re.sub('<[^<]+?>', '', entry.summary).split("전체 기사 보기")[0]
                detailed_summary = f"{rss_desc} (본문 직접 추출이 제한되어 뉴스 요약을 제공합니다.)"

            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": detailed_summary.strip(),
                "link": entry.link
            })
    except Exception as e:
        print(f"목록 수집 에러: {e}")
            
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
        body {{ background: #f1f5f9; font-family: 'Pretendard', sans-serif; color: #1e293b; }}
        .header {{ 
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 60px 20px; 
            text-align: center; color: white; border-bottom: 5px solid #38bdf8; margin-bottom: 40px;
        }}
        .designer {{ border: 1.5px solid #38bdf8; color: #38bdf8; display: inline-block; padding: 4px 16px; border-radius: 50px; margin-bottom: 15px; font-weight: 600; }}
        .news-grid {{ max-width: 900px; margin: 0 auto; padding: 0 15px 80px; }}
        .news-card {{ 
            background: #fff; border-radius: 25px; padding: 35px; margin-bottom: 30px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
            text-decoration: none; display: block; color: inherit; transition: all 0.3s;
        }}
        .news-card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); border-color: #38bdf8; }}
        .badge-media {{ background: #eff6ff; color: #1d4ed8; font-weight: 800; padding: 6px 14px; border-radius: 10px; font-size: 0.9rem; }}
        .card-title {{ font-size: 1.5rem; font-weight: 800; color: #0f172a; margin: 20px 0 15px; line-height: 1.4; letter-spacing: -0.5px; }}
        .card-desc {{ font-size: 1.1rem; color: #334155; line-height: 1.9; text-align: justify; background: #f8fafc; padding: 25px; border-radius: 15px; border: 1px dashed #cbd5e1; }}
        .footer {{ text-align: center; color: #64748b; padding-bottom: 60px; font-size: 0.95rem; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="designer">Designed by chipdory.hwang</div>
        <h1 class="fw-bold mb-3">Tech Intelligence Deep Dive</h1>
        <p class="opacity-75 mb-0">오늘의 반도체 · AI · IT · 과학 기술 핵심 리포트</p>
        <p class="small mt-2 opacity-50">업데이트: {today}</p>
    </header>
    <div class="news-grid">
    """
    for i, news in enumerate(news_data):
        html_content += f"""
        <a href="{news['link']}" target="_blank" class="news-card">
            <div class="d-flex justify-content-between align-items-center">
                <span class="badge-media">{news['media']}</span>
                <span style="color:#f1f5f9; font-weight:900; font-size:3rem;">{i+1:02d}</span>
            </div>
            <div class="card-title">{news['title']}</div>
            <div class="card-desc">{news['desc']}</div>
            <div class="mt-3 text-end" style="color:#1d4ed8; font-weight:700;">본문 전체보기 →</div>
        </a>
        """
    html_content += """
    </div>
    <div class="footer">본 리포트는 인공지능이 매일 아침 뉴스를 분석하여 생성합니다.</div>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
