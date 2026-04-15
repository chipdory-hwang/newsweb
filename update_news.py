import feedparser
import datetime
import ssl
import re
import requests
from bs4 import BeautifulSoup

# 보안 설정
ssl._create_default_https_context = ssl._create_unverified_context

def get_full_summary(url):
    """기사 원문 링크에서 본문을 가져와 요약함"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 본문 텍스트 추출 (p 태그 위주)
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text() for p in paragraphs if len(p.get_text()) > 30])
        
        content = re.sub(r'\s+', ' ', content).strip()
        if len(content) > 350:
            return content[:350] + "..."
        return content if len(content) > 50 else None
    except:
        return None

def get_latest_news():
    all_news = []
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

            # 본문 요약 가져오기
            detailed_desc = get_full_summary(entry.link)
            if not detailed_desc:
                detailed_desc = re.sub('<[^<]+?>', '', entry.summary).split("전체 기사 보기")[0]

            all_news.append({
                "media": media,
                "title": title.strip(),
                "desc": detailed_desc.strip(),
                "link": entry.link # 기사 원문 링크 저장
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
        body {{ background: #f8f9fa; font-family: 'Pretendard', sans-serif; color: #212529; }}
        .header {{ 
            background: #ffffff; padding: 50px 20px; border-bottom: 8px solid #0056b3;
            text-align: center; margin-bottom: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .designer {{ color: #0056b3; font-weight: 700; border: 2px solid #0056b3; display: inline-block; padding: 4px 15px; border-radius: 5px; margin-bottom: 15px; }}
        .news-grid {{ max-width: 900px; margin: 0 auto; padding: 0 15px 80px; }}
        
        /* 카드 디자인 및 링크 설정 */
        .news-card {{ 
            background: #fff; border-radius: 20px; padding: 35px; margin-bottom: 30px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.08); border-left: 8px solid #0056b3;
            text-decoration: none; display: block; color: inherit; transition: all 0.2s ease-in-out;
        }}
        .news-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.12); border-left-color: #003d7a; }}
        
        .badge-media {{ background: #f1f8ff; color: #0056b3; font-weight: 800; padding: 6px 16px; border-radius: 30px; font-size: 0.9rem; }}
        .card-title {{ font-size: 1.4rem; font-weight: 800; color: #1a1a1a; margin: 20px 0 15px; line-height: 1.4; }}
        .card-desc {{ font-size: 1.05rem; color: #444; line-height: 1.9; text-align: justify; border-top: 1px solid #f0f0f0; padding-top: 15px; }}
        .read-more {{ margin-top: 15px; display: inline-block; color: #0056b3; font-weight: 700; font-size: 0.95rem; }}
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
            <div class="read-more">원문 기사 읽기 →</div>
        </a>
        """
    html_content += """
    </div>
    <div class="footer">매일 아침 6시, 딥다이브 리포트가 업데이트됩니다.</div>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = get_latest_news()
    update_html(data)
