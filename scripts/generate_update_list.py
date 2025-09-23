import requests
from bs4 import BeautifulSoup
from pathlib import Path

def fetch_stage_title(stage_id: str) -> str:
    url = f"https://ponosgames.com/information/appli/battlecats/stage/{stage_id}.html"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        r.encoding = 'utf-8'  # 文字コードをUTF-8に固定
        soup = BeautifulSoup(r.text, "html.parser")
        h2 = soup.find("h2")
        return h2.text.strip() if h2 else "(タイトル取得失敗)"
    except Exception as e:
        return f"(取得失敗: {e})"

def main():
    # ステージIDリストを読み込む
    with open("stage_ids.txt", "r") as f:
        stage_ids = f.read().split()

entries = []
for sid in stage_ids:
    title = fetch_stage_title(sid)  # 個別にタイトル取得
    pdf_url = f"https://shibanban2.github.io/bc-event/stage2/{sid[0]}/{sid}.pdf"  # 個別PDF
    entries.append(f"<li>{sid} {title} — <a href='{pdf_url}'>PDF</a></li>")


    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>更新ステージ一覧</title>
</head>
<body>
  <h1>更新されたステージ一覧</h1>
  <ul>
    {''.join(entries)}
  </ul>
</body>
</html>
"""

    Path("update").mkdir(exist_ok=True)
    Path("update/index.html").write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()
