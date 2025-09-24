import os
import sys
import base64
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Chrome 起動設定（グローバルに使う）
options = Options()
options.add_argument("--headless=new")  # headless モード
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

def save_stage_pdf(stage_code):
    # Chrome はスレッドごとに新規起動
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 保存先フォルダ
        category = ''.join([c for c in stage_code if c.isalpha()])
        save_dir = os.path.join("stage2", category)
        os.makedirs(save_dir, exist_ok=True)

        url = f"https://ponosgames.com/information/appli/battlecats/stage/{stage_code}.html"
        print(f"[INFO] {stage_code} を処理中: {url}")

        driver.get(url)

        # 必要な要素が出るまで待機（最大10秒）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "stage0_enemy_list"))
        )

        # 非表示部分を強制展開
        driver.execute_script("""
            setCurrentStageIndex(120);
            for (let i = 0; i < 120; i++) {
                enableData('stage' + i + '_enemy_list');
                enableData('stage' + i + '_enemy_list_1');
                enableData('stage' + i + '_no_continue');
            }
        """)

        # PDF 出力
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
        pdf_bytes = base64.b64decode(pdf_data['data'])
        out_path = os.path.join(save_dir, f"{stage_code}.pdf")
        with open(out_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"[OK] 保存完了: {out_path}")
    except Exception as e:
        print(f"[WARN] {stage_code} でエラー: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_pdf.py S410 [S411 ...]")
        sys.exit(1)

    stage_codes = sys.argv[1:]

    # 並列処理（最大5並列で処理）
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(save_stage_pdf, stage_codes)

    print("[DONE] 全処理終了")

