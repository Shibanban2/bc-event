import os
import sys
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def save_stage_pdf(stage_code):
    # 保存先の親フォルダ決定（英字部分すべてを使用してND/SR対応）
    category = ''.join([c for c in stage_code if c.isalpha()])
    save_dir = os.path.join("stage2", category)
    os.makedirs(save_dir, exist_ok=True)

    url = f"https://ponosgames.com/information/appli/battlecats/stage/{stage_code}.html"
    print(f"[INFO] {stage_code} を処理中: {url}")

    driver.get(url)
    time.sleep(2)

    # 非表示部分を強制展開
    driver.execute_script("""
        setCurrentStageIndex(120);
        for (let i = 0; i < 120; i++) {
            enableData('stage' + i + '_enemy_list');
            enableData('stage' + i + '_enemy_list_1');
            enableData('stage' + i + '_no_continue');
        }
    """)
    time.sleep(1)

    # PDF 出力
    pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
    pdf_bytes = base64.b64decode(pdf_data['data'])
    out_path = os.path.join(save_dir, f"{stage_code}.pdf")
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"[OK] 保存完了: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf.py S410 [S411 ...]")
        sys.exit(1)

    stage_codes = sys.argv[1:]

    # Chrome 起動設定
    options = Options()
    options.add_argument("--headless=new")  # headless モード
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    for code in stage_codes:
        try:
            save_stage_pdf(code)
        except Exception as e:
            print(f"[WARN] {code} でエラー: {e}")

    driver.quit()
    print("[DONE] 全処理終了")
