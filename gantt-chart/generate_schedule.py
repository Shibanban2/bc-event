import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import to_rgba
from datetime import datetime, timedelta
import aiohttp
import asyncio
import random

# ================== 共通関数 ==================
async def fetch_tsv(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch {url}: Status {resp.status}")
                    return []
                text = await resp.text()
                lines = text.splitlines()
                rows = []
                for line in lines:
                    row = line.split("\t")
                    if "".join(row).strip() == "":
                        continue
                    while len(row) > 0 and row[-1] == "":
                        row.pop()
                    if len(row) == 0 or (row[-1] not in ("0", "1")):
                        row = row + ["0"]
                    rows.append(row)
                return rows
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def format_date(d):
    return f"{str(d)[4:6]}/{str(d)[6:8]}"

def get_day_of_week(date_str):
    try:
        date = datetime.strptime(str(date_str), "%Y%m%d")
        days = ["月", "火", "水", "木", "金", "土", "日"]
        return days[date.weekday()]
    except ValueError:
        return ""

def parse_gatya_row(row, name_map, item_map, today_str):
    try:
        start_date = str(row[0])
        start_time = row[1]
        end_date = str(row[2])
        end_time = row[3]
        type_code = int(row[8]) if len(row) > 8 and row[8].isdigit() else 0
        j = int(row[9]) if len(row) > 9 and row[9].isdigit() else 0
    except:
        return []

    if end_date < today_str or end_date == "20300101":
        return []

    base_cols = {
        1: {"id": 10, "confirm": 21, "title": 24},
        2: {"id": 25, "confirm": 36, "title": 39},
        3: {"id": 40, "confirm": 51, "title": 54},
        4: {"id": 55, "confirm": 66, "title": 69},
        5: {"id": 70, "confirm": 81, "title": 84},
        6: {"id": 85, "confirm": 96, "title": 99},
        7: {"id": 100, "confirm": 111, "title": 114},
    }

    col = base_cols.get(j)
    if not col:
        return []

    try:
        id = int(row[col["id"]]) if len(row) > col["id"] and row[col["id"]].isdigit() else -1
        confirm = "【確定】" if len(row) > col["confirm"] and row[col["confirm"]] == "1" and type_code != 4 else ""
    except:
        return []

    if id <= 0:
        return []

    gname = name_map.get(id, f"error[{id}]")
    label = f"{gname} {confirm}"
    return [(start_date, end_date, label)]

# ================== メイン処理 ==================
async def main():
    # データ取得
    gatya_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/token/gatya.tsv")
    name_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/token/gatyaName.tsv")
    item_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/token/gatyaitem.tsv")

    name_map = {int(r[0]): r[1] for r in name_rows if r and r[0].isdigit()}
    item_map = {int(r[2]): r[3] for r in item_rows if r and len(r) > 3 and r[2].isdigit()}

    today_str = datetime.now().strftime("%Y%m%d")
    events = []
    for row in gatya_rows[1:]:
        events.extend(parse_gatya_row(row, name_map, item_map, today_str))

    if not events:
        print("No events found")
        return

    # パステルカラー生成
    pastel_colors = [
        "#AEC6CF", "#FFB347", "#B39EB5", "#77DD77",
        "#FFD1DC", "#CBAACB", "#FF6961", "#FDFD96",
        "#CB99C9", "#F0E68C"
    ]
    random.shuffle(pastel_colors)

    # 日付範囲決定
    start_dates = [datetime.strptime(sd, "%Y%m%d") for sd, _, _ in events]
    end_dates = [datetime.strptime(ed, "%Y%m%d") for _, ed, _ in events]
    min_date = min(start_dates)
    max_date = max(end_dates)

    fig, ax = plt.subplots(figsize=(12, len(events)*0.5))

    # 土日の背景
    curr = min_date
    while curr <= max_date:
        if curr.weekday() >= 5:  # 土日
            ax.axvspan(curr, curr + timedelta(days=1), color=to_rgba('pink', 0.2))
        curr += timedelta(days=1)

    ylabels = []
    for i, (sd, ed, label) in enumerate(events):
        start = datetime.strptime(sd, "%Y%m%d")
        end = datetime.strptime(ed, "%Y%m%d")
        color = pastel_colors[i % len(pastel_colors)]
        ax.barh(i, (end - start).days + 1, left=start, color=color, edgecolor='black')
        ylabels.append(label)

    ax.set_yticks(range(len(events)))
    ax.set_yticklabels(ylabels, fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d(%a)"))  # 29(金) 形式
    ax.set_xlim(min_date - timedelta(days=1), max_date + timedelta(days=1))
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    fig.autofmt_xdate(rotation=0)
    plt.tight_layout()
    plt.savefig("schedule.png", dpi=150)
    print("schedule.png generated!")

if __name__ == "__main__":
    asyncio.run(main())
