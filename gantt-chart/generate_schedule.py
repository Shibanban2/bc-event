import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import to_rgba
from datetime import datetime, timedelta
import aiohttp
import asyncio
import random
import matplotlib.font_manager as fm

# ================== 共通関数 ==================
async def fetch_tsv(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch {url}: Status {resp.status}")
                    return []
                text = await resp.text(encoding='utf-8')  # UTF-8で文字化け対策
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

def get_day_of_week_jp(date_str):
    date = datetime.strptime(date_str, "%Y%m%d")
    days = ["月", "火", "水", "木", "金", "土", "日"]
    return days[date.weekday()]

def parse_gatya_row(row, name_map, today_str):
    try:
        start_date = str(row[0])
        end_date = str(row[2])
        j = int(row[9]) if len(row) > 9 and row[9].isdigit() else 0
        col_id = {1:10,2:25,3:40,4:55,5:70,6:85,7:100}.get(j)
        confirm_col = {1:21,2:36,3:51,4:66,5:81,6:96,7:111}.get(j)
        if col_id is None or len(row) <= col_id:
            return []
        id = int(row[col_id]) if row[col_id].isdigit() else -1
        confirm = "【確定】" if len(row) > confirm_col and row[confirm_col] == "1" else ""
        if id <= 90 or end_date < today_str or end_date == "20300101":
            return []
        name = name_map.get(id, f'error[{id}]')
        if name in ["プラチナガチャ", "レジェンドガチャ"]:
            return []
        label = f"{name} {confirm}"
        return [(start_date, end_date, label, id)]
    except:
        return []

# ================== メイン処理 ==================
async def main():
    # 日本語フォント設定
    plt.rcParams["font.family"] = "IPAexGothic"  # 環境に応じて

    # データ取得
    gatya_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/token/gatya.tsv")
    name_rows = await fetch_tsv("https://raw.githubusercontent.com/Shibanban2/bc-event/main/token/gatyaName.tsv")
    name_map = {int(r[0]): r[1] for r in name_rows if r and r[0].isdigit()}

    today_str = datetime.now().strftime("%Y%m%d")
    events = []
    for row in gatya_rows[1:]:
        events.extend(parse_gatya_row(row, name_map, today_str))

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

    # 日付範囲
    start_dates = [datetime.strptime(sd, "%Y%m%d") for sd, _, _, _ in events]
    end_dates = [datetime.strptime(ed, "%Y%m%d") for _, ed, _, _ in events]
    min_date = min(start_dates)
    max_date = max(end_dates)
    num_days = (max_date - min_date).days + 1
    all_dates = [min_date + timedelta(days=i) for i in range(num_days)]

    fig, ax = plt.subplots(figsize=(num_days*0.5 + 5, len(events)*0.5))

    # 土日の背景
    for d in all_dates:
        if d.weekday() >= 5:
            ax.axvspan(d, d + timedelta(days=1), color=to_rgba("pink", 0.2))

    # イベントバー（縦軸は上が古い日程）
    ylabels = []
    for i, (sd, ed, label, _) in enumerate(reversed(events)):
        start = datetime.strptime(sd, "%Y%m%d")
        end = datetime.strptime(ed, "%Y%m%d")
        color = pastel_colors[i % len(pastel_colors)]
        ax.barh(i, (end - start).days + 1, left=start, color=color, edgecolor='black')
        ylabels.append(label)

    ax.set_yticks(range(len(events)))
    ax.set_yticklabels(ylabels, fontsize=9)
    ax.invert_yaxis()  # 上が古い日程
    ax.set_xticks(all_dates)
    ax.set_xticklabels([f"{d.day}({get_day_of_week_jp(d.strftime('%Y%m%d'))})" for d in all_dates], rotation=0)
    ax.xaxis.set_ticks_position('top')  # 横軸を上側
    ax.xaxis.set_label_position('top')
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("schedule.png", dpi=150)
    print("schedule.png generated!")

if __name__ == "__main__":
    asyncio.run(main())
