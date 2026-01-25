import livepopulartimes
import csv
import os
import random
import time
from datetime import datetime
import pytz
from tenacity import retry, stop_after_attempt, wait_fixed

# 🎯 目标名单
TARGETS = {
    "District": "District Pizza Palace, 2325 S Eads St, Arlington, VA", 
    "Dominos":  "Domino's Pizza, 3535 South Ball St, Arlington, VA 22202",
    "Papa":     "Papa John's Pizza, 1014 S Glebe Rd, Arlington, VA 22204",
    "Wiseguy":  "Wiseguy Pizza, 710 12th St S, Arlington, VA 22202",
    "WePizza":  "We, The Pizza, 2110 Crystal Dr, Arlington, VA 22202"
}

LIVE_FILE = 'pizza_data.csv'
TZ = pytz.timezone('America/New_York')

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_data(address):
    return livepopulartimes.get_populartimes_by_address(address)

def get_usual_popularity(data, current_dt):
    """🧠 智能分析：获取'平时这个时候'的平均热度"""
    try:
        # Google 返回的数据通常是周一(0)到周日(6)
        day_idx = current_dt.weekday() 
        hour_idx = current_dt.hour
        
        # 获取当天的历史数据列表 (24个小时)
        pop_times = data.get('populartimes', [])
        if not pop_times: return 0
        
        # 提取当前小时的平均值
        usual = pop_times[day_idx]['data'][hour_idx]
        return usual
    except:
        return 0

def run_spy():
    batch_time = datetime.now(TZ)
    batch_time_str = batch_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"🕵️‍♂️ Mission Start: {batch_time_str}")
    
    current_batch = []
    
    for code_name, address in TARGETS.items():
        try:
            time.sleep(random.randint(2, 5)) 
            data = fetch_data(address)
            
            # 1. 获取实时热度
            live_pop = data.get('current_popularity', 0) or 0
            
            # 2. 获取平时热度 (历史平均)
            usual_pop = get_usual_popularity(data, batch_time)
            
            # 3. 计算偏差 (异常指数)
            gap = live_pop - usual_pop
            
            rating = data.get('rating', 0)
            
            print(f"📍 {code_name} | Live: {live_pop} | Usual: {usual_pop} | Gap: {gap}")
            
            # 💾 存入 CSV
            current_batch.append([batch_time_str, code_name, live_pop, rating, usual_pop, gap])

        except Exception as e:
            print(f"❌ Error {code_name}: {e}")
            # 出错补零，保持数据连续
            current_batch.append([batch_time_str, code_name, 0, 0, 0, 0])
            continue

    # 追加写入
    file_exists = os.path.isfile(LIVE_FILE)
    with open(LIVE_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists: 
            writer.writerow(['Timestamp (ET)', 'Name', 'Live Popularity', 'Rating', 'Usual Popularity', 'Gap'])
        writer.writerows(current_batch)
    print("✅ Pizza Data Saved.")

if __name__ == "__main__":
    run_spy()
