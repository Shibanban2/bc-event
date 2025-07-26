let data = {};
const now = new Date();

// JSONデータ取得
fetch('https://Shibanban2.github.io/bc-event/data.json')
  .then(res => res.json())
  .then(json => {
    data = json;
    renderContent('gatya4', false);
  });

// 日付抽出してDate型に変換
function parseStartDate(text) {
  const match = text.match(/^(\d{2})\/(\d{2})/);
  if (!match) return null;
  const year = new Date().getFullYear();
  const month = parseInt(match[1]) - 1;
  const day = parseInt(match[2]);
  return new Date(year, month, day);
}

// イベントを日付順ソート（item4対応）
function sortEvents(eventArray, isObjectArray = false) {
  return eventArray
    .map(item => {
      const text = isObjectArray ? item.title : item;
      const match = text.match(/^(\d{2})\/(\d{2})/);
      const date = match
        ? new Date(now.getFullYear(), parseInt(match[1]) - 1, parseInt(match[2]))
        : new Date(2100, 0, 1); // 日付なしは最後
      return isObjectArray ? { ...item, date } : { text, date };
    })
    .sort((a, b) => a.date - b.date);
}

// コンテンツ描画
function renderContent(id, showPast) {
  const container = document.getElementById(id);
  container.innerHTML = '';

  const sections = id === 'all' ? Object.keys(data).filter(k => k !== 'gatya5') : [id];

  for (const key of sections) {
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = key;
    container.appendChild(title);

    if (!data[key] || data[key].length === 0) {
      const none = document.createElement('div');
      none.textContent = '表示できるイベントはありません';
      container.appendChild(none);
      continue;
    }

    // item4 はオブジェクト配列としてソート、それ以外は通常配列
    const isItem4 = key === 'item4';
    const sortedEvents = sortEvents(data[key], isItem4);
    let count = 0;

    for (let i = 0; i < sortedEvents.length; i++) {
      const event = sortedEvents[i];
      const text = isItem4 ? event.title : event.text || event;

      // gatya4: プラチナガチャ/レジェンドガチャを非表示
      if (key === 'gatya4' && (/プラチナガチャ|レジェンドガチャ/.test(text))) continue;

      // item3: 道場報酬 / 報酬設定（地底迷宮）を非表示
      if (key === 'item3' && (/道場報酬|報酬設定（地底迷宮）/.test(text))) continue;

      const startDate = parseStartDate(text);
      if (!showPast && startDate && startDate < now) continue;
      if (!showPast && !startDate) continue;

      const div = document.createElement('div');
      div.className = 'event-card';

      // 色付けルール
      if (!/ミッション/.test(text)) {
        if (/確定|レジェンドクエスト|風雲にゃんこ塔|異界にゃんこ塔|グランドアビス|闇目|ねこの目洞窟|ガチャ半額リセット|確率2倍|にゃんこスロット|必要/.test(text)) {
          div.classList.add('red');
        } else if (/step|異次元コロシアム|ランキングの間|ネコ基地トーク/.test(text)) {
          div.classList.add('blue');
        }
      }

      div.innerHTML = text;

      // モーダル対応
      if (key === 'gatya4') {
        div.addEventListener('click', () => {
          const detail = data.gatya5 && data.gatya5[i] ? data.gatya5[i] : '詳細情報がありません';
          openModal(detail);
        });
      }
      if (key === 'item4') {
        div.addEventListener('click', () => {
          const detail = event.detail || '詳細情報がありません';
          openModal(detail);
        });
      }

      container.appendChild(div);
      count++;
    }

    if (count === 0) {
      const none = document.createElement('div');
      none.textContent = '表示できるイベントはありません';
      container.appendChild(none);
    }
  }
}

// タブ切替
function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));

  document.querySelector(`.tab[onclick="showTab('${id}')"]`).classList.add('active');
  document.getElementById(id).classList.remove('hidden');

  renderContent(id, document.getElementById('showAll').checked);
}

// チェックボックスで過去イベント表示切替
document.getElementById('showAll').addEventListener('change', () => {
  const activeTab = document.querySelector('.tab.active').textContent.trim();
  const id = activeTab === 'すべての予定' ? 'all' : activeTab;
  renderContent(id, document.getElementById('showAll').checked);
});

// モーダル関連
function openModal(content) {
  document.getElementById('modal-body').innerHTML = content;
  document.getElementById('detail-modal').classList.add('show');
}

function closeModal() {
  document.getElementById('detail-modal').classList.remove('show');
}

document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('detail-modal').addEventListener('click', e => {
  if (e.target.id === 'detail-modal') closeModal();
});

// スクショ保存
document.getElementById('save-btn').addEventListener('click', () => {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const fileName = `nyanko_schedule_${yyyy}-${mm}-${dd}.png`;

  html2canvas(document.body, {
    backgroundColor: '#ffffff',
    useCORS: true
  }).then(canvas => {
    const link = document.createElement('a');
    link.download = fileName;
    link.href = canvas.toDataURL('image/png');
    link.click();
  });
});
