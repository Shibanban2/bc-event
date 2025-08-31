import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import requests

# TSVのURL
GATYA_TSV = "https://shibanban2.github.io/bc-event/token/gatya.tsv"
GATYA_NAME_TSV = "https://raw.githubusercontent.com/Shibanban2/bc-event/main/token/gatyaName.tsv"

# ガチャ名辞書を作成
name_map = {}
resp = requests.get(GATYA_NAME_TSV)
for line in resp.text.splitlines():
    if not line.strip():
        continue
    cols = line.split("\t")
    if len(cols) >= 2:
        try:
            name_map[int(cols[0])] = cols[1]
        except:
            pass

# TSV読み込み
df = pd.read_csv(GATYA_TSV, sep="\t", header=None)

# 必要な列だけ使う (開始日, 終了日, ガチャID)
df = df[[0, 2, 4]]
df.columns = ["start", "end", "gacha_id"]

# 日付を変換
df["start"] = pd.to_datetime(df["start"], format="%Y%m%d")
df["end"] = pd.to_datetime(df["end"], format="%Y%m%d")

# IDを名前に変換
df["gacha_name"] = df["gacha_id"].map(name_map).fillna(df["gacha_id"].astype(str))

# 描画準備
fig, ax = plt.subplots(figsize=(12, 6))

for i, row in df.iterrows():
    ax.barh(row["gacha_name"], (row["end"] - row["start"]).days,
            left=row["start"], height=0.6, alpha=0.7)
    ax.text(row["start"], i, row["gacha_name"], va="center", ha="right", fontsize=9)

# 今日の縦線
today = datetime.datetime.today()
ax.axvline(today, color="red", linestyle="--")

# 日付フォーマット
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
plt.xticks(rotation=45)

plt.title("ガチャスケジュール", fontsize=14)
plt.tight_layout()

# PNG保存
plt.savefig("schedule.png")
print("✅ schedule.png を出力しました")
