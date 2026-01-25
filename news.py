import feedparser
import csv
import os
from datetime import datetime
import pytz

# --- 配置区 ---
TZ = pytz.timezone('America/New_York')
RSS_URL = "https://news.google.com/rss/search?q=Pentagon+US+Defense&hl=en-US&gl=US&ceid=US:en"
NEWS_FILE = 'pentagon_news.csv'

def run_news_spy():
    print("📰 Starting News Wire...")
    try:
        # 设置超时防止卡死
        feed = feedparser.parse(RSS_URL)
        news_items = []
        
        # 只取最新的 10 条
        for entry in feed.entries[:10]:
            title = entry.title.split(' - ')[0] # 去掉媒体后缀
            source = entry.source.title if 'source' in entry else 'Unknown'
            link = entry.link
            
            # 处理时间
            if hasattr(entry, 'published_parsed'):
                dt = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc)
                local_dt = dt.astimezone(TZ)
                time_str = local_dt.strftime('%H:%M')
                date_str = local_dt.strftime('%Y-%m-%d')
            else:
                now = datetime.now(TZ)
                time_str = now.strftime('%H:%M')
                date_str = now.strftime('%Y-%m-%d')

            news_items.append([date_str, time_str, source, title, link])
            print(f"   📡 Found: {title[:20]}...")
        
        # 覆盖写入 (只保留最新情报)
        if news_items:
            with open(NEWS_FILE, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Time', 'Source', 'Title', 'Link'])
                writer.writerows(news_items)
            print(f"✅ News Data Saved ({len(news_items)} items).")
        else:
            print("⚠️ No news items found.")
            
    except Exception as e:
        print(f"❌ News Error: {e}")

if __name__ == "__main__":
    run_news_spy()
