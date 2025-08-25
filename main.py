function parseGatya() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("gatya");
  const gData = ss.getSheetByName("GData");
  const verSheet = ss.getSheetByName("ver");
  const output = ss.getSheetByName("gatya4");
  output.clear();

  const rows = sheet.getDataRange().getValues();
  const gDataValues = gData.getRange("A:D").getValues();
  const verValues = verSheet.getRange("A1:A20").getValues().flat();

  const result = [];

  // GData検索用
  function lookupName(id) {
    const entry = gDataValues.find(r => r[0] == id);
    return entry ? entry[1] : `error [${id}] is not found...`;
  }
  function lookupExtra(code) {
    const entry = gDataValues.find(r => r[2] == code);
    return entry ? entry[3] : "";
  }

  // バージョン表記
  function formatVer(num) {
    const major = Math.floor(num / 10000);
    const minor = Math.floor((num % 10000) / 100);
    const patch = num % 100;
    return `${major}.${minor}.${patch}`;
  }

  function formatDate(d) {
    if (d == 20300101) return "#永続";
    return `${String(d).slice(4, 6)}/${String(d).slice(6, 8)}`;
  }

  function formatTime(t) {
    if (!t || t == 0 || t == 1100) return ""; // 11:00 は省略
    const hour = String(Math.floor(t / 100)).padStart(2, "0");
    const min = String(t % 100).padStart(2, "0");
    return `${hour}:${min}`;
  }

  function formatRate(val) {
    if (!val || val == 0) return "";
    return String(val);  // ％ではなくそのまま数値で出力
  }

 for (let i = 1; i < rows.length; i++) {
  const row = rows[i];
  if (row[0] === "[end]") break;

  const startDate = formatDate(row[0]);
  const startTime = formatTime(row[1]);
  const endDate = formatDate(row[2]);
  const endTime = formatTime(row[3]);
  const minVer = row[4];
  const maxVer = row[5];
  const typeCode = row[8];
  const j = row[9];

  let type = "";
  switch (typeCode) {
    case 0: type = "ノーマルガチャ"; break;
    case 1: type = "通常レアガチャ"; break;
    case 4: type = "イベントガチャ"; break;
    default: type = "不明";
  }

  // 特例: I列=4 かつ J列=2
  if (typeCode == 4 && j == 2) {
    const id = row[27];
    const normal = formatRate(row[31]);
    const rare = formatRate(row[33]);
    const superRare = formatRate(row[35]);
    const ultraRare = formatRate(row[37]);
    const legend = formatRate(row[39]);
    const title = [row[40], row[41], row[42]].filter(Boolean).join("");
    const extraInfo = lookupExtra(row[28]); // 付属情報

    const dateRange = `${startDate}${startTime ? `(${startTime})` : ""}〜${endDate}${endTime ? `(${endTime})` : ""}`;

    let verText = "";
    if (minVer && !verValues.includes(minVer)) verText += `[要Ver.${formatVer(minVer)}]`;
    if (maxVer && maxVer != 999999) verText += `[Ver.${formatVer(maxVer)}まで]`;

    const colA = `${dateRange} ${lookupName(id)}${extraInfo ? " " + extraInfo : ""}${verText}`;
    const colK = `${dateRange} ${lookupName(id)}${verText}`; // lookupExtra を除いた内容

    result.push([
      colA, type, id, normal, rare, superRare, ultraRare, legend, j, title, colK
    ]);
    continue;
  }

  // jごとの列位置
  const baseCols = {
    1: { id: 10, extra: 13, normal: 14, rare: 16, super: 18, ultra: 20, confirm: 21, legend: 22, title: 24 },
    2: { id: 25, extra: 28, normal: 29, rare: 31, super: 33, ultra: 35, confirm: 36, legend: 37, title: 39 },
    3: { id: 40, extra: 43, normal: 44, rare: 46, super: 48, ultra: 50, confirm: 51, legend: 52, title: 54 },
    4: { id: 55, extra: 58, normal: 59, rare: 61, super: 63, ultra: 65, confirm: 66, legend: 67, title: 69 },
    5: { id: 70, extra: 73, normal: 74, rare: 76, super: 78, ultra: 80, confirm: 81, legend: 82, title: 84 },
    6: { id: 85, extra: 88, normal: 89, rare: 91, super: 93, ultra: 95, confirm: 96, legend: 97, title: 99 },
    7: { id: 100, extra: 103, normal: 104, rare: 106, super: 108, ultra: 110, confirm: 111, legend: 112, title: 114 },
  };
  const col = baseCols[j];
  if (!col) continue;

  const id = row[col.id];
  const titleName = lookupName(id);
  const extraInfo = lookupExtra(row[col.extra]);
  const normal = formatRate(row[col.normal]);
  const rare = formatRate(row[col.rare]);
  const superRare = formatRate(row[col.super]);
  const ultraRare = formatRate(row[col.ultra]);
  const confirm = (row[col.confirm] == 1 && type !== "イベントガチャ") ? "【確定】" : "";
  const legend = formatRate(row[col.legend]);
  const title = row[col.title] || "";

  let verText = "";
  if (minVer && !verValues.includes(minVer)) verText += `[要Ver.${formatVer(minVer)}]`;
  if (maxVer && maxVer != 999999) verText += `[Ver.${formatVer(maxVer)}まで]`;

  const dateRange = `${startDate}${startTime ? `(${startTime})` : ""}〜${endDate}${endTime ? `(${endTime})` : ""}`;
  const colA = `${dateRange} ${titleName}${extraInfo ? " " + extraInfo : ""}${confirm}${verText}`;
  const colK = `${dateRange} ${titleName}${confirm}${verText}`; // lookupExtra を除く

  result.push([
    colA, type, id, normal, rare, superRare, ultraRare, legend, j, title, colK
  ]);
}

// 出力（K列は11列目）
output.getRange(1, 1, result.length, 11).setValues(result);
}
