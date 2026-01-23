import livepopulartimes
import csv
import os
import random
import time
import requests
import subprocess
from datetime import datetime
import pytz

# 🎯 战略监测名单
TARGETS = [
    "District Pizza Palace, 2325 S Eads St, Arlington, VA", 
    "Domino's Pizza, 3535 South Ball St, Arlington, VA 22202",
    "Papa John's Pizza, 1014 S Glebe Rd, Arlington, VA 22204",
    "Wiseguy Pizza, 710 12th St S, Arlington, VA 22202",
    "We, The Pizza, 2110 Crystal Dr, Arlington, VA 22202"
]

FILENAME = 'pizza_data.csv'

def send_discord_alert(shop_name, popularity, time_str):
    """发送手机报警 (Discord)"""
    webhook_url = os.environ.get('DISCORD_WEBHOOK')
    if not webhook_url:
        print("⚠️ No Discord Webhook configured.")
        return

    data = {
        "content": "@everyone 🚨 **五角大楼情报警报** 🚨",
        "embeds": [{
            "title": f"异常检测: {shop_name}",
            "description": "发现深夜异常人流活动，请密切关注国际局势！",
            "color": 16711680, # 红色
            "fields": [
                {"name": "当前热度", "value": str(popularity), "inline": True},
                {"name": "当地时间", "value": time_str, "inline": True}
            ],
            "footer": {"text": "Pentagon Pizza Watch System"}
        }]
    }
    try:
        requests.post(webhook_url, json=data)
        print(f"📱 Discord alert sent for {shop_name}!")
    except Exception as e:
        print(f"Failed to send Discord alert: {e}")

def send_github_alert(shop_name, popularity, time_str):
    """发送 GitHub Issue 报警"""
    title = f"⚠️ 警告: 五角大楼披萨指数异常! [{shop_name}]"
    body = f"### 侦测到异常活动\n- **店铺**: {shop_name}\n- **当前热度**: {popularity}\n- **时间**: {time_str}"
    try:
        subprocess.run(["gh", "issue", "create", "--title", title, "--body", body], check=True)
        print(f"🚨 GitHub Issue created for {shop_name}!")
    except Exception as e:
        print(f"Failed to send GitHub alert: {e}")

def run_spy():
    tz = pytz.timezone('America/New_York')
    print(f"🕵️‍♂️ Mission Start: Tracking {len(TARGETS)} locations...")

    for place in TARGETS:
        dc_now = datetime.now(tz)
        now_str = dc_now.strftime('%Y-%m-%d %H:%M:%S')
        current_hour = dc_now.hour
        
        try:
            # 防封机制：随机等待
            delay = random.randint(10, 20)
            time.sleep(delay)

            data = livepopulartimes.get_populartimes_by_address(place)
            name = data.get('name', place).split(",")[0]
            current_pop = data.get('current_popularity', 0) or 0
            rating = data.get('rating', 0)
            
            print(f"📍 {name} | Pop: {current_pop} | Hour: {current_hour}")

            # ==========================
            # 🚨 报警逻辑
            # ==========================
            # 这里的逻辑是：深夜(22点-5点) 且 热度>40 就报警
            is_night = (current_hour >= 22 or current_hour <= 5)
            is_busy = (current_pop > 40) 

            # 👇 如果您想现在立刻测试报警，把下面这行前面的 # 去掉，并把上面两行注释掉：
            # if True: 

            if is_night and is_busy:
                print(f"🔥 ANOMALY DETECTED: {name}")
                send_github_alert(name, current_pop, now_str)
                send_discord_alert(name, current_pop, now_str)
            
            # 写入 CSV
            file_exists = os.path.isfile(FILENAME)
            with open(FILENAME, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Timestamp (ET)', 'Name', 'Live Popularity', 'Rating'])
                writer.writerow([now_str, name, current_pop, rating])
                
        except Exception as e:
            print(f"❌ Error on {place}: {e}")
            continue

if __name__ == "__main__":
    run_spy()
