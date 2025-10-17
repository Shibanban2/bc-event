import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.patches import FancyBboxPatch
from matplotlib.dates import date2num
from datetime import datetime, timedelta
import aiohttp
import asyncio
import matplotlib.font_manager as fm

# ================== フォント設定だ　=================
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

# ================== 祝日取得 ==================
async def fetch_holidays(year):
    url = f"https://holidays-jp.github.io/api/v1/{year}/date.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Failed to fetch holidays for {year}: Status {resp.status}")
                return set()
            data = await resp.json()
            return set(data.keys())  # "YYYY-MM-DD" 形式

# ================== 曜日取得 ==================
def get_day_of_week_jp(date_str):
    date = datetime.strptime(date_str, "%Y%m%d")
    days = ["月", "火", "水", "木", "金", "土", "日"]
    return days[date.weekday()]

# ================== ガチャ行パース ==================
def parse_gatya_row(row, name_map, yesterday_str): # today_strをyesterday_strに変更
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
        
        # 修正: 終了日が昨日より前のイベントは除外（つまり、昨日を含むそれ以降に終了するイベントを表示）
        if id <= 90 or end_date == "20300101" or end_date < yesterday_str:
            return []
            
        name = name_map.get(str(id), f'error[{id}]')
        if name in ["プラチナガチャ", "レジェンドガチャ"]:
            return []
        label = f"{name} {confirm}"
        return [(start_date, end_date, start_time, end_time, label)]
    except:
        return []

# ================== 角丸バー描画 ==================
def draw_rounded_bar(ax, y, start_dt, width_days, color):
    start_num = date2num(start_dt)
    rect = FancyBboxPatch(
        (start_num, y - 0.4), width_days, 0.8,
        boxstyle="round,pad=0.02",
        linewidth=0.5,               # 縁を細く
        edgecolor="#555555",          # 黒の彩度を落とした色
        facecolor=to_rgba(color, 0.7) # 色を少し薄めて優しい感じ
    )
    ax.add_patch(rect)

# ================== メイン処理 ==================
async def main():
    set_japanese_font()

    # ---- TSV読み込み ----
    gatya_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/token/gatya.tsv")
    name_rows = await fetch_tsv("https://shibanban2.github.io/bc-event/name.tsv")
    name_map = {r[0]: r[1] for r in name_rows if len(r) >= 2}

    # 修正: フィルタリング基準を「昨日」にする
    yesterday = datetime.now().date() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y%m%d")
    
    events = []
    for row in gatya_rows[1:]:
        events.extend(parse_gatya_row(row, name_map, yesterday_str))

    if not events:
        print("No events found")
        return

    # ---- 色リスト ----
    pastel_colors = [
        "#BFD8B8", "#FFE0A3", "#C4B7E5", "#A8E6CF", "#FFCBC1", "#E0BBE4",
        "#FFF5BA", "#D5ECC2", "#FFDAC1", "#E0F7FA", "#F6C6EA", "#C2F0FC",
        "#F9F3CC", "#C8E6C9", "#FFD3B6", "#E1BEE7", "#B2EBF2", "#FFABAB",
        "#D7CCC8", "#F8BBD0", "#DCEDC8", "#FFCDD2", "#CFD8DC", "#F0F4C3"
    ]

    # ---- 日付範囲 ----
    start_dates = [datetime.strptime(sd, "%Y%m%d") for sd, _, _, _, _ in events]
    end_dates = [datetime.strptime(ed, "%Y%m%d") for _, ed, _, _, _ in events]
    min_date = min(start_dates) - timedelta(days=1)
    max_date = max(end_dates) + timedelta(days=1)
    num_days = (max_date - min_date).days + 1
    all_dates = [min_date + timedelta(days=i) for i in range(num_days)]

    # ---- 祝日データ取得 ----
    holidays = await fetch_holidays(min_date.year) | await fetch_holidays(max_date.year)

    # ---- 図のサイズ設定 ----
    dpi = 100
    fig_width = 700 / dpi
    fig_height = 400 / dpi
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

    tick_positions = [date2num(d) for d in all_dates]

    # ---- 土日 + 祝日背景を塗る ----
    for d in all_dates:
        date_str_dash = d.strftime("%Y-%m-%d")
        if d.weekday() in [5, 6] or date_str_dash in holidays:
            start = date2num(d)
            end = date2num(d + timedelta(days=1))
            ax.axvspan(start, end, color=to_rgba("pink", 0.2), zorder=0)

    # ---- 日付ラベル ----
    rotation_angle = 45 if num_days >= 14 else 0
    
    # 日付ラベルをマスの真ん中に配置
    tick_positions_centered = [pos + 0.5 for pos in tick_positions]
    ax.set_xticks(tick_positions_centered) 
    
    ax.set_xticklabels(
        [f"{d.day}({get_day_of_week_jp(d.strftime('%Y%m%d'))})" for d in all_dates],
        rotation=rotation_angle, ha="center", fontsize=9
    )
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    # ---- イベント棒描画 ----
    ylabels = []
    for i, (sd, ed, stime, etime, label) in enumerate(events):
        start = datetime.strptime(sd, "%Y%m%d")
        end = datetime.strptime(ed, "%Y%m%d")
        start_offset = timedelta(days=stime / 2400) if stime != 0 else timedelta(0)
        end_offset = timedelta(days=etime / 2400) if etime != 0 else timedelta(0)
        left = start + start_offset
        duration = (end + end_offset - start + timedelta(seconds=1)).total_seconds() / 86400 # 終了時刻を含めるための微調整を削除し、純粋な期間計算に変更（timedelta(seconds=1)は削除）
        duration = (end + end_offset - start + timedelta(days=1) - start_offset).total_seconds() / 86400 # 日付だけのイベントが1日分になるよう+1日補正し、開始オフセットを引く
        
        # 期間が0以下になる場合は、期間を1日として処理するか、ここではイベントを表示しない
        if duration <= 0:
            duration = 1.0 # 期間が計算上ゼロやマイナスになる場合の最小補正

        draw_rounded_bar(ax, i + 1, left, duration, pastel_colors[i % len(pastel_colors)])
        ylabels.append(label)
        

    # ---- 軸設定 ----
    ax.set_yticks(range(len(events) + 2))  # +2 で上下に余白
    ax.set_yticklabels([""] + ylabels + [""], fontsize=9)  # 最初と最後を空白ラベルに
    ax.tick_params(axis='x', labelsize=9)
    ax.invert_yaxis()
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    # ---- 今日の位置に赤い点線 ----
    ax.set_xlim(date2num(min_date), date2num(max_date))
    # 現在時刻ではなく、今日の真夜中の位置に線を引き、ずれを修正
    today_num = date2num(datetime.now().date()) 
    ax.axvline(
        today_num,                    # 今日の日付の始まりをX座標に
        color="red",                  # 赤色
        linestyle="--",               # 点線
        linewidth=1.2,                # 線の太さ
        zorder=5                      # バーより前に出す
    )


    # ---- 左下にクレジット追加 ----
    fig.text(
        0.01, 0.01, "https://x.com/bcevent_bot",
        ha="left", va="bottom", fontsize=8, color="gray"
    )

    plt.tight_layout()
    plt.savefig("schedule.png", dpi=dpi)
    print("✅ schedule.png generated!")

if __name__ == "__main__":
    asyncio.run(main())
