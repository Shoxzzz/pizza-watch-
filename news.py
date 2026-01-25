import feedparser
import csv
import os
from datetime import datetime
import pytz

# --- 战术配置区 ---
TZ = pytz.timezone('America/New_York')

# 🔥 V37 核心升级：战术级新闻过滤器
# 1. 必须包含：Pentagon 加上 (军事 或 战争 或 冲突 或 警报 或 部队)
# 2. 必须排除：预算(-budget) 和 合同(-contract) -> 我们只关心打仗，不关心花钱
# 3. 时间限制：when:2d (只看最近48小时)
RSS_URL = "https://news.google.com/rss/search?q=Pentagon+(military+OR+war+OR+conflict+OR+alert+OR+troops)+-budget+-contract+when:2d&hl=en-US&gl=US&ceid=US:en"

NEWS_FILE = 'pentagon_news.csv'

def run_news_spy():
    print("📡 Scanning Military Frequencies...")
    try:
        # 设置 socket 超时防止卡死
        feed = feedparser.parse(RSS_URL)
        news_items = []
        
        # 只提取前 8 条最高优先级的
        for entry in feed.entries[:8]:
            try:
                # 清洗标题 (去掉 ' - The New York Times' 这种后缀)
                title = entry.title.split(' - ')[0] 
                source = entry.source.title if 'source' in entry else 'INTEL'
                link = entry.link
                
                # 时间标准化
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
                print(f"   🎯 Target Acquired: {title[:30]}...")
            
            except Exception as item_e:
                continue
        
        # 覆盖写入 (保证情报实时性)
        if news_items:
            with open(NEWS_FILE, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Time', 'Source', 'Title', 'Link'])
                writer.writerows(news_items)
            print(f"✅ Intel Secured: {len(news_items)} reports.")
        else:
            print("⚠️ No tactical updates found.")
            
    except Exception as e:
        print(f"❌ Comms Failure: {e}")

if __name__ == "__main__":
    run_news_spy()
