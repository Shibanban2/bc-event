import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from datetime import datetime, timedelta
import aiohttp
import asyncio
import matplotlib.font_manager as fm

# ================== フォント設定 ==================
def set_japanese_font():
    plt.rcParams["font.family"] = "IPAPGothic"
    print("✅ 使用フォント: IPAPGothic")

# ================== TSV取得 ==================
async def fetch_tsv(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Failed to fetch {url}: Status {resp.status}")
                return []
            text = await resp.text(encoding='utf-8')
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

def get_day_of_week_jp(date_str):
    date = datetime.strptime(date_str, "%Y%m%d")
    days = ["月", "火", "水", "木", "金", "土", "日"]
    return days[date.weekday()]

def parse_gatya_row(row, name_map, today_str):
    try:
        start_date = str(row[0])
        end_date = str(row[2])
        start_time = int(row[1]) if row[1].isdigit() else 0
        end_time = int(row[3]) if row[3].isdigit() else 0
        j = int(row[9]) if len(row) > 9 and row[9].isdigit() else 0
        col_id = {1:10,2:25,3:40,4:55,5:70,6:85,7:100}.get(j)
        confirm_col = {1:21,2:36,3:51,4:66,5:81,6:96,7:111}.get(j)
        if col_id is None or len(row) <= col_id:
            return []
        id = int(row[col_id]) if row[col_id].isdigit() else -1
        confirm = "【確定】" if len(row) > confirm_col and row[confirm_col] == "1" else ""
        if id <= 90 or end_date == "20300101" or start_date < today_str:
            return []
        name = name_map.get(id, f'error[{id}]')
        if name in ["プラチナガチャ", "レジェンドガチャ"]:
            return []
        label = f"{name} {confirm}"
        return [(start_date, end_date, start_time, end_time, label)]
    except:
        return []

# ================== メイン処理 ==================
async def main():
    set_japanese_font()

    gatya_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/token/gatya.tsv")
    name_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/token/gatyaName.tsv")
    name_map = {int(r[0]): r[1] for r in name_rows if r and r[0].isdigit()}

    today_str = datetime.now().strftime("%Y%m%d")
    events = []
    for row in gatya_rows[1:]:
        events.extend(parse_gatya_row(row, name_map, today_str))

    if not events:
        print("No events found")
        return

    pastel_colors = [
        "#BFD8B8", "#FFE0A3", "#C4B7E5", "#A8E6CF",
        "#FFCBC1", "#E0BBE4", "#FFF5BA", "#D5ECC2",
        "#FFDAC1", "#E0F7FA"
    ]

    start_dates = [datetime.strptime(sd, "%Y%m%d") for sd, _, _, _, _ in events]
    end_dates = [datetime.strptime(ed, "%Y%m%d") for _, ed, _, _, _ in events]
    min_date = min(start_dates)
    max_date = max(end_dates)
    num_days = (max_date - min_date).days + 1
    all_dates = [min_date + timedelta(days=i) for i in range(num_days)]

    fig, ax = plt.subplots(figsize=(num_days*0.5 + 5, len(events)*0.5))

    for d in all_dates:
        if d.weekday() >= 5:
            ax.axvspan(d, d + timedelta(days=1), color=to_rgba("pink", 0.2))

    ylabels = []
    for i, (sd, ed, stime, etime, label) in enumerate(events):
        start = datetime.strptime(sd, "%Y%m%d")
        end = datetime.strptime(ed, "%Y%m%d")
        start_offset = stime / 2400 if stime != 0 else 0
        end_offset = etime / 2400 if etime != 0 else 1
        ax.barh(i, (end - start).days + end_offset - start_offset, left=start + timedelta(days=start_offset), 
                color=pastel_colors[i % len(pastel_colors)], edgecolor='black')
        ylabels.append(label)

    ax.set_yticks(range(len(events)))
    ax.set_yticklabels(ylabels, fontsize=9)
    ax.set_xticks(all_dates)
    ax.set_xticklabels([f"{d.day}({get_day_of_week_jp(d.strftime('%Y%m%d'))})" for d in all_dates], rotation=0)
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')
    ax.invert_yaxis()
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("schedule.png", dpi=150)
    print("✅ schedule.png generated!")

if __name__ == "__main__":
    asyncio.run(main())
