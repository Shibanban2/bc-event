import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from io import StringIO

# TSV URL
URL = "https://bc-event.vercel.app/token/gatya.tsv"

# TSVを取得
response = requests.get(URL)
if response.status_code != 200:
    raise Exception(f"Failed to fetch TSV: Status code {response.status_code}")

# TSVをデータフレームに変換
tsv_data = StringIO(response.text)
df = pd.read_csv(tsv_data, sep='\t')

# 今日の日付 (2025/08/25 19:56 JST)
today = datetime.now().strftime("%Y%m%d")

# ガチャデータをフィルタリング (終了日が今日以降かつ永続でない)
gacha_data = df.iloc[1:].query("`2` >= @today and `2` != 20300101").copy()

# 補助関数
def format_date(d):
    if d == 20300101:
        return "#永続"
    return f"{str(d)[4:6]}/{str(d)[6:8]}"

def format_time(t):
    try:
        t = int(t)
        hour = str(t // 100).zfill(2)
        min = str(t % 100).zfill(2)
        return f"{hour}:{min}"
    except (ValueError, TypeError):
        return "00:00"

def get_day_of_week(date_str):
    try:
        date = datetime.strptime(str(date_str), "%Y%m%d")
        days = ["月", "火", "水", "木", "金", "土", "日"]
        return days[date.weekday()]
    except ValueError:
        return ""

def lookup_name(id, name_map):
    return name_map.get(str(id), f"error[{id}]")

# 名前マップの準備 (gatyaName.tsv から取得)
name_url = "https://shibanban2.github.io/bc-event/token/gatyaName.tsv"
name_response = requests.get(name_url)
if name_response.status_code != 200:
    raise Exception(f"Failed to fetch gatyaName.tsv: Status code {name_response.status_code}")

name_tsv = StringIO(name_response.text)
name_df = pd.read_csv(name_tsv, sep='\t', header=None)
name_map = dict(zip(name_df[0].astype(str), name_df[1]))

# ガチャスケジュールを整形
gacha_schedule = []
for _, row in gacha_data.iterrows():
    start_date = format_date(row[0])
    start_time = format_time(row[1])
    end_date = format_date(row[2])
    end_time = format_time(row[3])
    type_code = int(row[8]) if pd.notna(row[8]) else 0
    j = int(row[9]) if pd.notna(row[9]) else 0

    # 特例: typeCode=4 かつ j=2
    if type_code == 4 and j == 2:
        id = row[27] if pd.notna(row[27]) else -1
    else:
        base_cols = {
            1: 10, 2: 25, 3: 40, 4: 55, 5: 70, 6: 85, 7: 100
        }
        id = row[base_cols.get(j, -1)] if pd.notna(base_cols.get(j, -1)) else -1

    if id <= 0 or pd.isna(id):
        continue

    gacha_name = lookup_name(id, name_map)
    date_range = f"{start_date}({get_day_of_week(row[0])}) {start_time}〜{end_date}({get_day_of_week(row[2])}) {end_time}"
    schedule_line = f"{date_range}\n　{id} {gacha_name}"
    gacha_schedule.append(schedule_line)

# 画像生成
plt.figure(figsize=(10, 6))
plt.title("ガチャスケジュール", fontsize=16, color='white')
plt.xlabel("日付", fontsize=12, color='white')
plt.ylabel("ガチャ名", fontsize=12, color='white')
plt.xticks(color='white')
plt.yticks(color='white')
plt.gca().set_facecolor('#1a1a1a')
plt.gcf().set_facecolor('#1a1a1a')

dates = [line.split('\n')[0] for line in gacha_schedule]
names = [line.split('\n')[1].replace('　', '').split(' ', 1)[1] for line in gacha_schedule]

plt.barh(names, [1] * len(names), color=['#ff9999', '#66b3ff'], align='center')
for i, (date, name) in enumerate(zip(dates, names)):
    plt.text(0.5, i, date, ha='center', va='center', color='white')

# 画像を表示
plt.tight_layout()
plt.show()

# 必要に応じて保存
# plt.savefig("gacha_schedule.png", dpi=100, bbox_inches='tight')
