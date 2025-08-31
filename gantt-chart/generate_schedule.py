import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import aiohttp
import asyncio

# ========== Discord bot から移植した共通関数 ==========
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

def format_time(t):
    try:
        t = int(t)
        return f"{str(t // 100).zfill(2)}:{str(t % 100).zfill(2)}"
    except:
        return "00:00"

def get_day_of_week(date_str):
    try:
        date = datetime.strptime(str(date_str), "%Y%m%d")
        days = ["月", "火", "水", "木", "金", "土", "日"]
        return days[date.weekday()]
    except ValueError:
        return ""

def lookup_extra(code, item_map):
    try:
        return item_map.get(int(code), "")
    except:
        return ""

def parse_gatya_row(row, name_map, item_map, today_str):
    output_lines = []
    try:
        start_date = str(row[0])
        start_time = row[1]
        end_date = str(row[2])
        end_time = row[3]
        type_code = int(row[8]) if len(row) > 8 and row[8].isdigit() else 0
        j = int(row[9]) if len(row) > 9 and row[9].isdigit() else 0
    except:
        return output_lines

    if end_date < today_str or end_date == "20300101":
        return output_lines

    base_cols = {
        1: {"id": 10, "extra": 13, "confirm": 21, "title": 24},
        2: {"id": 25, "extra": 28, "confirm": 36, "title": 39},
        3: {"id": 40, "extra": 43, "confirm": 51, "title": 54},
        4: {"id": 55, "extra": 58, "confirm": 66, "title": 69},
        5: {"id": 70, "extra": 73, "confirm": 81, "title": 84},
        6: {"id": 85, "extra": 88, "confirm": 96, "title": 99},
        7: {"id": 100, "extra": 103, "confirm": 111, "title": 114},
    }

    col = base_cols.get(j)
    if not col:
        return output_lines

    try:
        id = int(row[col["id"]]) if len(row) > col["id"] and row[col["id"]].isdigit() else -1
        extra = lookup_extra(row[col["extra"]], item_map) if len(row) > col["extra"] else ""
        confirm = "【確定】" if len(row) > col["confirm"] and row[col["confirm"]] == "1" and type_code != 4 else ""
    except:
        return output_lines

    if id <= 0:
        return output_lines

    gname = name_map.get(id, f"error[{id}]")
    date_range = f"{format_date(start_date)}({get_day_of_week(start_date)}) {format_time(start_time)}〜{format_date(end_date)}({get_day_of_week(end_date)}) {format_time(end_time)}"
    col_k = f"{date_range}\n{id} {gname}{confirm}"
    if extra:
        col_k += f" {extra}"
    output_lines.append((start_date, end_date, col_k))
    return output_lines

# ========== メイン処理 ==========
async def main():
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

    # matplotlib で簡単なガントチャート風に描画
    fig, ax = plt.subplots(figsize=(10, len(events) * 0.4))
    ylabels = []
    for i, (sd, ed, label) in enumerate(events):
        start = datetime.strptime(sd, "%Y%m%d")
        end = datetime.strptime(ed, "%Y%m%d")
        ax.barh(i, (end - start).days + 1, left=start, color="skyblue")
        ylabels.append(label)
    ax.set_yticks(range(len(events)))
    ax.set_yticklabels(ylabels, fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig("schedule.png")

if __name__ == "__main__":
    asyncio.run(main())
