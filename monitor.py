import livepopulartimes
import csv
import os
import random
import time
import requests
from datetime import datetime
import pytz
from tenacity import retry, stop_after_attempt, wait_fixed

# 🎯 强制字典：{ "写入CSV的代号": "Google搜索地址" }
# 这里的 Key (左边的词) 绝对不要改！它就是我们在前端显示的 ID
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

def run_spy():
    # 🕒 统一时间戳：一次抓取，所有店用同一个由时间，确保前端线条对其
    batch_time = datetime.now(TZ)
    batch_time_str = batch_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"🕵️‍♂️ Mission Start: {batch_time_str}")
    
    current_batch = []
    
    # 遍历字典：key 是代号，addr 是地址
    for code_name, address in TARGETS.items():
        try:
            time.sleep(random.randint(1, 3)) 
            data = fetch_data(address)
            
            # 无论 Google 返回什么名字，我们只存 code_name (例如 "Dominos")
            # 这样前端就能完美匹配中文了！
            pop = data.get('current_popularity', 0) or 0
            rating = data.get('rating', 0)
            
            print(f"📍 {code_name} | Pop: {pop}")
            current_batch.append([batch_time_str, code_name, pop, rating])

        except Exception as e:
            print(f"❌ Error {code_name}: {e}")
            continue

    if current_batch:
        file_exists = os.path.isfile(LIVE_FILE)
        with open(LIVE_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists: 
                writer.writerow(['Timestamp (ET)', 'Name', 'Live Popularity', 'Rating'])
            writer.writerows(current_batch)

if __name__ == "__main__":
    run_spy()
