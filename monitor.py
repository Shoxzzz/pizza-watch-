import livepopulartimes
import csv
import os
import random
import time
from datetime import datetime
import pytz

def run_spy():
    # 🎯 战略监测名单 (共5家)
    targets = [
        "District Pizza Palace, 2325 S Eads St, Arlington, VA",  # 深夜指标核心
        "Domino's Pizza, 3535 South Ball St, Arlington, VA 22202", # 官方外卖主力
        "Papa John's Pizza, 1014 S Glebe Rd, Arlington, VA 22204", # 侧翼补充
        "Wiseguy Pizza, 710 12th St S, Arlington, VA 22202",       # 五角大楼城人流指标
        "We, The Pizza, 2110 Crystal Dr, Arlington, VA 22202"      # 水晶城承包商据点
    ]
    
    filename = 'pizza_data.csv'
    # 设定为美东时间 (五角大楼当地时间)
    tz = pytz.timezone('America/New_York')
    
    print(f"🕵️‍♂️ Mission Start: Tracking {len(targets)} locations...")

    for place in targets:
        now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # 🛑 防封逻辑：模拟人类查看地图的随机停顿 (10-25秒)
            delay = random.randint(10, 25)
            print(f"⏳ Waiting {delay}s...")
            time.sleep(delay)

            # 抓取数据
            print(f"📍 Checking: {place}")
            data = livepopulartimes.get_populartimes_by_address(place)
            
            # 提取关键数据
            name = data.get('name', place).split(",")[0] # 只取店名，不要长地址
            current_pop = data.get('current_popularity', 0)
            rating = data.get('rating', 0)
            
            # 修正空值
            if current_pop is None: 
                current_pop = 0

            print(f"✅ Result: {name} | Pop: {current_pop}")

            # 写入 CSV
            file_exists = os.path.isfile(filename)
            with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['Timestamp (ET)', 'Name', 'Live Popularity', 'Rating'])
                writer.writerow([now, name, current_pop, rating])
                
        except Exception as e:
            print(f"❌ Error on {place}: {e}")
            continue # 出错不停止，继续查下一家

if __name__ == "__main__":
    run_spy()
