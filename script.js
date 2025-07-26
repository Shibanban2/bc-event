let data = {};
const now = new Date();

fetch('https://Shibanban2.github.io/bc-event/data.json')
  .then(res => res.json())
  .then(json => {
    data = json;
    renderContent('gatya4', false);
  });

function parseStartDate(text) {
  const match = text.match(/^(\d{2})\/(\d{2})/);
  if (!match) return null;
  const year = new Date().getFullYear();
  const month = parseInt(match[1]) - 1;
  const day = parseInt(match[2]);
  return new Date(year, month, day);
}

// イベント表示処理
function renderContent(id, showPast) {
  const container = document.getElementById(id);
  container.innerHTML = '';

  // item4 の A列（イベント名）と D列（詳細）を分けて処理するための準備
  const isItem4 = id === 'item4';
  const item4Names = isItem4 ? (data.item4?.names || []) : [];
  const item4Details = isItem4 ? (data.item4?.details || []) : [];

  const sections = id === 'all'
    ? Object.keys(data).filter(k => k !== 'gatya5')  // gatya5 は詳細用なので表示しない
    : [id];

  for (const key of sections) {
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = key;
    container.appendChild(title);

    let count = 0;
    const events = sortEvents(data[key] || []);

    for (let i = 0; i < events.length; i++) {
      const text = events[i];
      if (key === 'gatya4' && (/プラチナガチャ|レジェンドガチャ/.test(text))) continue;

      // item4: 道場報酬 / 報酬設定（地底迷宮） を非表示
      if (key === 'item4' && (/道場報酬|報酬設定（地底迷宮）/.test(text))) continue;

      const startDate = parseStartDate(text);
      if (!showPast && startDate && startDate < now) continue;
      if (!showPast && !startDate) continue;

      const div = document.createElement('div');
      div.className = 'event-card';

      if (!/ミッション/.test(text)) {
        if (/祭|確定|レジェンドクエスト|風雲にゃんこ塔|異界にゃんこ塔|グランドアビス|闇目|ねこの目洞窟|ガチャ半額リセット|確率2倍|にゃんこスロット|必要/.test(text)) {
          div.classList.add('red');
        } else if (/おまけアップ|異次元コロシアム|強襲|ランキングの間|ネコ基地トーク/.test(text)) {
          div.classList.add('blue');
        }
      }

      div.innerHTML = text;

      // gatya4 と item4 でモーダルの内容を取得
      if (key === 'gatya4') {
        div.addEventListener('click', () => {
          const detail = data.gatya5[i] || '詳細情報がありません';
          openModal(detail);
        });
      }
      if (key === 'item4') {
        div.addEventListener('click', () => {
          const detail = item4Details[i] || '詳細情報がありません';
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

// 日付順にソート
function sortEvents(keyArray) {
  return keyArray
    .map(text => {
      const match = text.match(/^(\d{2})\/(\d{2})/);
      if (!match) return { text, date: new Date(2100, 0, 1) }; // 日付なしは最後へ
      const year = now.getFullYear();
      const month = parseInt(match[1]) - 1;
      const day = parseInt(match[2]);
      return { text, date: new Date(year, month, day) };
    })
    .sort((a, b) => a.date - b.date)
    .map(obj => obj.text);
}

function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));

  document.querySelector(`.tab[onclick="showTab('${id}')"]`).classList.add('active');
  document.getElementById(id).classList.remove('hidden');

  renderContent(id, document.getElementById('showAll').checked);
}

document.getElementById('showAll').addEventListener('change', () => {
  const activeTab = document.querySelector('.tab.active').textContent.trim();
  const id = activeTab === 'すべての予定' ? 'all' : activeTab;
  renderContent(id, document.getElementById('showAll').checked);
});

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
