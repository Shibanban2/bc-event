const puppeteer = require("puppeteer");
const fs = require("fs");

async function generate(stageIdsStr) {
  const stageIds = stageIdsStr.split(",").map(s => s.trim());
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  for (const id of stageIds) {
    const url = `https://ponosgames.com/information/appli/battlecats/stage/${id}.html`;
    console.log(`Fetching ${url}...`);
    await page.goto(url, { waitUntil: "networkidle2" });

    // 隠し要素を展開
    await page.evaluate(() => {
      setCurrentStageIndex(120);
      for (let i = 0; i < 120; i++) {
        enableData("stage" + i + "_enemy_list");
        enableData("stage" + i + "_enemy_list_1");
        enableData("stage" + i + "_no_continue");
      }
    });

    // 保存先
    const dir = `public/stage2/${id[0]}`;
    fs.mkdirSync(dir, { recursive: true });

    await page.pdf({ path: `${dir}/${id}.pdf`, format: "A4" });
    console.log(`Saved ${dir}/${id}.pdf`);
  }

  await browser.close();
}

generate(process.argv[2]);

