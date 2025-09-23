import requests
from bs4 import BeautifulSoup
from pathlib import Path

def fetch_stage_title(stage_id: str) -> str:
    url = f"https://ponosgames.com/information/appli/battlecats/stage/{stage_id}.html"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        r.encoding = r.apparent_encoding  # 文字コードを自動判定
        soup = BeautifulSoup(r.text, "html.parser")
        h2 = soup.find("h2")
        return h2.text.strip() if h2 else "(タイトル取得失敗)"
    except Exception as e:
        return f"(取得失敗: {e})"

def main():
    # ステージIDリストを読み込む（空白・改行で分割）
    with open("stage_ids.txt", "r") as f:
        stage_ids = f.read().replace(",", " ").split()

    entries = []
    for sid in stage_ids:
        title = fetch_stage_title(sid)  # 個別にタイトル取得
        # フォルダは英字部分すべてを使用（ND/SR対応）
        category = ''.join([c for c in sid if c.isalpha()])
        pdf_url = f"https://shibanban2.github.io/bc-event/stage2/{category}/{sid}.pdf"
        entries.append(f"<li>{sid} {title} — <a href='{pdf_url}'>PDF</a></li>")

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>更新ステージ一覧</title>
  <style>
    body {{
      font-family: "Noto Sans JP", sans-serif;
      background: #f5f7fa;
      margin: 0;
      padding: 20px;
    }}
    h1 {{
      text-align: center;
      color: #333;
      margin-bottom: 30px;
    }}
    ul {{
      list-style: none;
      padding: 0;
      max-width: 800px;
      margin: 0 auto;
    }}
    li {{
      background: #fff;
      margin-bottom: 15px;
      padding: 15px 20px;
      border-radius: 12px;
      box-shadow: 0 3px 6px rgba(0,0,0,0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;
      transition: transform 0.2s;
    }}
    li:hover {{
      transform: translateY(-3px);
    }}
    .stage-id {{
      font-weight: bold;
      color: #007acc;
    }}
    .stage-title {{
      flex: 1;
      margin: 0 15px;
      color: #444;
    }}
    a {{
      text-decoration: none;
      color: #fff;
      background: #007acc;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 14px;
      transition: background 0.2s;
    }}
    a:hover {{
      background: #005f99;
    }}
  </style>
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

