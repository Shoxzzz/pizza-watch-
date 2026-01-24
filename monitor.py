import livepopulartimes
import csv
import os
import random
import time
import requests
import subprocess
from datetime import datetime, timedelta
import pytz
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_fixed # 👈 引入重试机制

# ================= 配置区 =================
TARGETS = [
    "District Pizza Palace, 2325 S Eads St, Arlington, VA", 
    "Domino's Pizza, 3535 South Ball St, Arlington, VA 22202",
    "Papa John's Pizza, 1014 S Glebe Rd, Arlington, VA 22204",
    "Wiseguy Pizza, 710 12th St S, Arlington, VA 22202",
    "We, The Pizza, 2110 Crystal Dr, Arlington, VA 22202"
]
LIVE_FILE = 'pizza_data.csv'
ARCHIVE_FILE = 'pizza_archive.csv'
TZ = pytz.timezone('America/New_York')
# =========================================

def send_discord_embed(title, desc, color, fields):
    """发送 Discord 富文本卡片 (通用版)"""
    webhook_url = os.environ.get('DISCORD_WEBHOOK')
    if not webhook_url: return
    
    data = {
        "embeds": [{
            "title": title,
            "description": desc,
            "color": color,
            "fields": fields,
            "footer": {"text": "🛡️ Pentagon Intel V5 | Black Ops System"},
            "timestamp": datetime.now().isoformat()
        }]
    }
    try: requests.post(webhook_url, json=data)
    except: pass

def send_daily_report(df, now_str):
    """📢 发送每日战报 (每天早上8点触发)"""
    # 获取过去24小时的数据
    cutoff = datetime.now(TZ) - timedelta(hours=24)
    # 这里我们简单取主文件里的数据做分析
    recent = df.tail(100) # 取最近100条近似
    
    max_row = recent.loc[recent['Live Popularity'].idxmax()]
    max_pop = max_row['Live Popularity']
    max_shop = max_row['Name']
    
    fields = [
        {"name": "📉 24H 最高峰值", "value": f"{max_shop}: **{max_pop}**", "inline": False},
        {"name": "✅ 系统状态", "value": "运行正常 (Online)", "inline": True},
        {"name": "📂 数据归档", "value": "自动执行中", "inline": True}
    ]
    
    send_discord_embed(
        "📅 每日情报简报 (Daily Briefing)", 
        f"指挥官，这是过去 24 小时的五角大楼周边活动汇总。\n报告时间: {now_str}",
        3066993, # 绿色
        fields
    )

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5)) # 👈 如果报错，自动重试3次，每次等5秒
def fetch_data(place):
    return livepopulartimes.get_populartimes_by_address(place)

def manage_data(current_batch):
    # 写入主文件
    file_exists = os.path.isfile(LIVE_FILE)
    with open(LIVE_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists: writer.writerow(['Timestamp (ET)', 'Name', 'Live Popularity', 'Rating'])
        writer.writerows(current_batch)

    # 数据归档逻辑 (保持轻量化)
    try:
        df = pd.read_csv(LIVE_FILE)
        # 如果正好是早上 8 点 (UTC 12:00 或 13:00)，发战报
        # 简单判断：如果当前批次包含 08:xx 的时间
        now = datetime.now(TZ)
        if now.hour == 8 and now.minute < 20: 
            send_daily_report(df, now.strftime('%Y-%m-%d %H:%M:%S'))

        # 归档逻辑 (同V4)
        df['dt'] = pd.to_datetime(df['Timestamp (ET)'])
        cutoff = datetime.now(TZ) - timedelta(days=7)
        cutoff = cutoff.replace(tzinfo=None)
        
        recent = df[df['dt'] >= cutoff].copy()
        old = df[df['dt'] < cutoff].copy()
        
        if not old.empty:
            old.drop(columns=['dt'], inplace=True)
            has_archive = os.path.isfile(ARCHIVE_FILE)
            old.to_csv(ARCHIVE_FILE, mode='a', header=not has_archive, index=False, encoding='utf-8-sig')
            
        recent.drop(columns=['dt'], inplace=True)
        recent.to_csv(LIVE_FILE, index=False, encoding='utf-8-sig')
    except Exception as e:
        print(f"⚠️ Data maintenance warning: {e}")

def run_spy():
    print(f"🕵️‍♂️ [V5 BLACK OPS] Mission Start: {datetime.now(TZ)}")
    current_batch = []
    
    for place in TARGETS:
        try:
            time.sleep(random.randint(2, 8)) # 稍微快一点，这就是效率
            data = fetch_data(place) # 调用带重试功能的函数
            
            name = data.get('name', place).split(",")[0]
            pop = data.get('current_popularity', 0) or 0
            rating = data.get('rating', 0)
            now = datetime.now(TZ)
            now_str = now.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"📍 {name} | Pop: {pop}")
            
            # 🚨 报警逻辑 V5 (增加 DEFCON 等级概念)
            is_night = (now.hour >= 22 or now.hour <= 5)
            
            if is_night and pop > 40:
                print(f"🔥 DEFCON 1: {name}")
                fields = [
                    {"name": "当前热度", "value": str(pop), "inline": True},
                    {"name": "判定", "value": "🚨 极度异常 (DEFCON 1)", "inline": True},
                    {"name": "时间", "value": now_str, "inline": False}
                ]
                send_discord_embed(f"⚠️ 紧急警报: {name}", "监测到深夜异常高人流！请立即核查新闻。", 15158332, fields)
            
            current_batch.append([now_str, name, pop, rating])

        except Exception as e:
            print(f"❌ Failed to track {place} after retries: {e}")
            continue

    if current_batch:
        manage_data(current_batch)

if __name__ == "__main__":
    run_spy()
