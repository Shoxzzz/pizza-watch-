import feedparser
import csv
import os
from datetime import datetime
import pytz

# 🎯 目标：Google News 实时聚合 (关键词：Pentagon)
RSS_URL = "https://news.google.com/rss/search?q=Pentagon+US+Defense&hl=en-US&gl=US&ceid=US:en"
CSV_FILE = 'pentagon_news.csv'
TZ = pytz.timezone('America/New_York')

def fetch_news():
    print("📡 Scanning Pentagon Frequencies...")
    feed = feedparser.parse(RSS_URL)
    
    news_items = []
    
    # 只取最新的 10 条
    for entry in feed.entries[:10]:
        try:
            # 清洗标题 (去掉 ' - Source' 后缀)
            title = entry.title.split(' - ')[0]
            source = entry.source.title if 'source' in entry else 'Unknown'
            link = entry.link
            
            # 处理时间
            if hasattr(entry, 'published_parsed'):
                # 把 UTC 转换成美东时间
                dt = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc)
                local_dt = dt.astimezone(TZ)
                time_str = local_dt.strftime('%H:%M')
                date_str = local_dt.strftime('%Y-%m-%d')
            else:
                time_str = datetime.now(TZ).strftime('%H:%M')
                date_str = datetime.now(TZ).strftime('%Y-%m-%d')

            news_items.append([date_str, time_str, source, title, link])
            print(f"✅ Found: {title[:30]}...")
            
        except Exception as e:
            print(f"⚠️ Skip: {e}")
            continue

    # 💾 暴力覆盖写入 (新闻我们要看最新的，不需要存历史)
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Time', 'Source', 'Title', 'Link'])
        writer.writerows(news_items)
    
    print("💾 Intel Saved to pentagon_news.csv")

if __name__ == "__main__":
    fetch_news()
