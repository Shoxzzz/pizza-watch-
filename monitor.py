import livepopulartimes
import csv
import os
import random
import time
from datetime import datetime
import pytz

def run_spy():
    # 目标：这里我设为了 District Pizza Palace，您也可以换成其他的
    target = "District Pizza Palace, 2325 S Eads St, Arlington, VA"
    
    # 设定文件名
    filename = 'pizza_data.csv'
    
    # 获取美东时间 (五角大楼时间)
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

    try:
        # 模拟人类的随机延迟（防止被谷歌秒封）
        delay = random.randint(5, 15)
        print(f"Waiting {delay} seconds...")
        time.sleep(delay)

        # 抓取数据
        print(f"Checking {target}...")
        data = livepopulartimes.get_populartimes_by_address(target)
        
        # 提取关键指标
        current_pop = data.get('current_popularity', 0) # 实时热度
        rating = data.get('rating', 0)
        
        if current_pop is None: 
            current_pop = 0

        print(f"Time: {now} | Pop: {current_pop}")

        # 写入 CSV
        file_exists = os.path.isfile(filename)
        # encoding='utf-8-sig' 保证Excel打开不乱码
        with open(filename, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp (ET)', 'Name', 'Live Popularity', 'Rating'])
            
            writer.writerow([now, data.get('name'), current_pop, rating])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_spy()
